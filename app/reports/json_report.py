import json
from typing import Dict, Any

def generate_json_report(report_data: Dict[str, Any]) -> str:
    """
    Serializes the research report data structure into a formatted JSON string.
    """
    return json.dumps(report_data, indent=2, ensure_ascii=False)
