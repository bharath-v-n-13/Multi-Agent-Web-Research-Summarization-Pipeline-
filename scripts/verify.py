import os
import json
import uuid
import sys
from pathlib import Path

def validate_report(file_path: Path) -> bool:
    print(f"Validating report: {file_path.name}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"  [ERROR] Failed to parse JSON: {e}")
        return False
        
    # Check required fields
    required_keys = ["report_id", "topic", "summary", "sections", "sources", "critique", "metadata"]
    for key in required_keys:
        if key not in data:
            print(f"  [ERROR] Missing required top-level key: '{key}'")
            return False
            
    # Validate report_id format
    report_id = data["report_id"]
    try:
        uuid.UUID(report_id)
    except ValueError:
        print(f"  [ERROR] Invalid UUID format for report_id: '{report_id}'")
        return False
        
    # Validate confidence score
    critique = data["critique"]
    confidence = critique.get("confidence_score")
    if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
        print(f"  [ERROR] Confidence score out of range (0.0-1.0): {confidence}")
        return False
        
    # Gather source_ids and urls for citation verification
    sources = data["sources"]
    valid_source_ids = set()
    valid_urls = set()
    for src in sources:
        if "source_id" in src:
            valid_source_ids.add(src["source_id"])
        if "url" in src:
            valid_urls.add(src["url"])
            
    # Validate citations in sections
    sections = data["sections"]
    if not isinstance(sections, list):
        print("  [ERROR] 'sections' must be a list")
        return False
        
    for i, sec in enumerate(sections):
        citations = sec.get("citations", [])
        for cite in citations:
            if cite not in valid_source_ids and cite not in valid_urls:
                print(f"  [ERROR] Section {i+1} ('{sec.get('heading')}') contains invalid citation: '{cite}'")
                return False
                
    # Validate metadata
    metadata = data["metadata"]
    if not isinstance(metadata.get("total_urls_visited"), int):
        print("  [ERROR] Metadata 'total_urls_visited' must be an integer")
        return False
    if not isinstance(metadata.get("agent_interactions"), int):
        print("  [ERROR] Metadata 'agent_interactions' must be an integer")
        return False
    if not isinstance(metadata.get("wall_clock_seconds"), (int, float)):
        print("  [ERROR] Metadata 'wall_clock_seconds' must be a number")
        return False
        
    print("  [OK] Valid schema and citations.")
    return True

def main():
    reports_dir = Path("reports")
    if not reports_dir.exists():
        print("No reports directory found. Run the pipeline first.")
        sys.exit(1)
        
    json_reports = list(reports_dir.glob("*.json"))
    if not json_reports:
        print("No JSON reports found to validate. Run a research request in JSON output format.")
        sys.exit(0)
        
    all_valid = True
    seen_ids = set()
    
    for r_path in json_reports:
        # Load and get ID for duplicate check
        try:
            with open(r_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)
                r_id = report_data.get("report_id")
                if r_id in seen_ids:
                    print(f"  [ERROR] Duplicate report_id detected: {r_id}")
                    all_valid = False
                seen_ids.add(r_id)
        except Exception:
            pass
            
        if not validate_report(r_path):
            all_valid = False
            
    if all_valid:
        print("\nAll generated JSON reports successfully verified.")
        sys.exit(0)
    else:
        print("\nSome reports failed verification.")
        sys.exit(1)

if __name__ == "__main__":
    main()
