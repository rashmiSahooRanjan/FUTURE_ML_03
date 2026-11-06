"""
Export Utilities for TalentRank AI
Converts candidates, ranking tables, and screening summaries into downloadable CSV and Excel streams.
"""

import io
from typing import List, Dict, Any
import pandas as pd

class ExportUtils:
    @staticmethod
    def to_csv_bytes(data: List[Dict[str, Any]]) -> bytes:
        """Converts list of dicts to CSV bytes."""
        df = pd.DataFrame(data)
        # Format list columns as comma-separated strings
        for col in df.columns:
            if df[col].dtype == object and df[col].apply(lambda x: isinstance(x, list)).any():
                df[col] = df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))
        return df.to_csv(index=False).encode('utf-8')

    @staticmethod
    def to_excel_bytes(data: List[Dict[str, Any]]) -> bytes:
        """Converts list of dicts to Excel bytes."""
        df = pd.DataFrame(data)
        for col in df.columns:
            if df[col].dtype == object and df[col].apply(lambda x: isinstance(x, list)).any():
                df[col] = df[col].apply(lambda x: ", ".join(x) if isinstance(x, list) else str(x))

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Screening Results")
        return buffer.getvalue()


export_utils = ExportUtils()
