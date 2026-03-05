"""
CSV Parser Service — Securely reads and previews CSV files.
"""

import os
import pandas as pd
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.abspath("./uploads")

class CSVParserService:
    def __init__(self):
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR, exist_ok=True)

    def get_preview(self, filename: str, rows: int = 5) -> Dict[str, Any]:
        """
        Reads a CSV file from the uploads directory and returns a preview.
        """
        # 1. Sanitize Path (Prevent Traversal)
        safe_path = os.path.normpath(os.path.join(UPLOAD_DIR, os.path.basename(filename)))
        
        if not safe_path.startswith(UPLOAD_DIR):
            return {"success": False, "error": "Access denied: Invalid file path."}

        if not os.path.exists(safe_path):
            return {"success": False, "error": f"File '{filename}' not found in uploads."}

        try:
            # 2. Limit File Size (e.g., 10MB)
            if os.path.getsize(safe_path) > 10 * 1024 * 1024:
                return {"success": False, "error": "File too large (Max 10MB)."}

            # 3. Read Preview
            df = pd.read_csv(safe_path, nrows=rows)
            summary = {
                "columns": list(df.columns),
                "preview": df.to_dict(orient="records"),
                "total_rows_estimate": "N/A (Preview only)"
            }
            return {"success": True, "data": summary}
            
        except Exception as e:
            logger.error(f"CSVParserService Error: {str(e)}")
            return {"success": False, "error": f"Failed to parse CSV: {str(e)}"}

csv_parser_service = CSVParserService()
