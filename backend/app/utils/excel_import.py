"""
Excel 导入工具
"""

import uuid
from datetime import datetime
from decimal import Decimal
from io import BytesIO
from typing import List, Dict, Any, Tuple

import pandas as pd
from openpyxl import load_workbook


class ExcelImportError(Exception):
    """Excel 导入错误"""

    def __init__(self, message: str, row: int = None, column: str = None):
        self.message = message
        self.row = row
        self.column = column
        super().__init__(self.message)


class CustomerExcelImporter:
    """客户 Excel 导入器"""

    # 必需字段
    REQUIRED_FIELDS = ["customer_code", "customer_name"]

    # 字段映射（支持中文列名）
    FIELD_MAPPING = {
        "客户编码": "customer_code",
        "客户名称": "customer_name",
        "行业": "industry_name",
        "客户等级": "level_code",
        "状态": "status",
        "联系人": "contact_person",
        "联系电话": "contact_phone",
        "联系邮箱": "contact_email",
        "地址": "address",
        "结算状态": "settlement_status",
        "负责人": "owner_username",
        "备注": "remark",
    }

    def __init__(self, file_content: bytes):
        """初始化导入器"""
        self.file_content = file_content
        self.errors: List[Dict[str, Any]] = []
        self.success_count = 0
        self.data: List[Dict[str, Any]] = []

    def parse(self) -> Tuple[List[Dict], List[Dict]]:
        """
        解析 Excel 文件

        Returns:
            (成功数据列表，错误列表)
        """
        try:
            # 读取 Excel
            df = pd.read_excel(
                BytesIO(self.file_content),
                engine="openpyxl",
            )

            # 重命名列
            df = self._rename_columns(df)

            # 验证和转换数据
            for index, row in df.iterrows():
                try:
                    validated = self._validate_row(
                        row, index + 2
                    )  # +2 因为 Excel 行号从 1 开始，且有表头
                    if validated:
                        self.data.append(validated)
                        self.success_count += 1
                except ExcelImportError as e:
                    self.errors.append(
                        {
                            "row": e.row,
                            "column": e.column,
                            "error": e.message,
                            "data": row.to_dict(),
                        }
                    )

            return self.data, self.errors

        except Exception as e:
            raise ExcelImportError(f"文件解析失败：{str(e)}")

    def _rename_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """重命名列"""
        # 先去除空列名
        df = df.rename(
            columns=lambda x: x.strip() if pd.notna(x) and isinstance(x, str) else x
        )

        # 应用字段映射
        rename_dict = {}
        for cn_name, en_name in self.FIELD_MAPPING.items():
            if cn_name in df.columns:
                rename_dict[cn_name] = en_name

        df = df.rename(columns=rename_dict)
        return df

    def _validate_row(self, row: pd.Series, row_num: int) -> Dict[str, Any] | None:
        """
        验证单行数据

        Args:
            row: 行数据
            row_num: 行号（用于错误报告）

        Returns:
            验证后的数据字典
        """
        result = {}

        # 检查必需字段
        for field in self.REQUIRED_FIELDS:
            value = row.get(field)
            if pd.isna(value) or str(value).strip() == "":
                raise ExcelImportError(
                    f"缺少必需字段：{field}",
                    row=row_num,
                    column=field,
                )
            result[field] = str(value).strip()

        # 可选字段处理
        if pd.notna(row.get("contact_person")):
            result["contact_person"] = str(row["contact_person"]).strip()

        if pd.notna(row.get("contact_phone")):
            result["contact_phone"] = str(row["contact_phone"]).strip()

        if pd.notna(row.get("contact_email")):
            result["contact_email"] = str(row["contact_email"]).strip()

        if pd.notna(row.get("address")):
            result["address"] = str(row["address"]).strip()

        if pd.notna(row.get("remark")):
            result["remark"] = str(row["remark"]).strip()

        # 状态字段转换
        status = row.get("status")
        if pd.notna(status):
            status_str = str(status).strip().lower()
            if status_str in ["active", "启用", "正常"]:
                result["status"] = "active"
            elif status_str in ["inactive", "禁用", "停用"]:
                result["status"] = "inactive"
            elif status_str in ["test", "测试"]:
                result["status"] = "test"
            else:
                result["status"] = "active"  # 默认

        # 结算状态转换
        settlement_status = row.get("settlement_status")
        if pd.notna(settlement_status):
            settlement_str = str(settlement_status).strip().lower()
            if settlement_str in ["settled", "已结算"]:
                result["settlement_status"] = "settled"
            else:
                result["settlement_status"] = "unsettled"

        # 保留外键引用名称（后续通过服务层解析为 ID）
        if pd.notna(row.get("industry_name")):
            result["industry_name"] = str(row["industry_name"]).strip()

        if pd.notna(row.get("level_code")):
            result["level_code"] = str(row["level_code"]).strip().upper()

        if pd.notna(row.get("owner_username")):
            result["owner_username"] = str(row["owner_username"]).strip()

        return result

    def get_summary(self) -> Dict[str, Any]:
        """获取导入摘要"""
        return {
            "success_count": self.success_count,
            "error_count": len(self.errors),
            "total_count": self.success_count + len(self.errors),
        }
