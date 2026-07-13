import re
from datetime import datetime, timezone
from typing import Dict, Any
from app.utils.logger import logger

class Scraper:
    """
    Simulates scraping and normalizes document content by extracting text,
    stripping HTML formatting, and adding standard metadata.
    """
    @staticmethod
    def clean_html(html_content: str) -> str:
        """
        Removes HTML tags, scripts, and style sheets while retaining clean text structure.
        """
        if not html_content:
            return ""
        
        # Remove script and style elements
        text = re.sub(r'<(script|style)\b[^>]*>([\s\S]*?)<\/\1>', ' ', html_content)
        # Remove comments
        text = re.sub(r'<!--[\s\S]*?-->', ' ', text)
        # Convert structural HTML blocks to newlines
        text = re.sub(r'<\/?(address|blockquote|dd|div|dl|dt|fieldset|form|h[1-6]|hr|li|ol|p|pre|table|tr|ul)\b[^>]*>', '\n', text)
        # Strip all other tags
        text = re.sub(r'<[^>]*>', ' ', text)
        # Decode basic entities if any
        text = text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        
        # Normalize multiple spaces (excluding newlines) to a single space
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Clean up whitespace and empty lines
        lines = [line.strip() for line in text.splitlines()]
        cleaned_text = '\n'.join([line for line in lines if line])
        return cleaned_text

    @classmethod
    def scrape(cls, raw_doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalizes a raw document dictionary.
        Extracts title, clean content, and tags it with a scrape timestamp.
        """
        url = raw_doc.get("url", "https://unknown-source.org")
        title = raw_doc.get("title", "Untitled Document")
        raw_content = raw_doc.get("content", "")
        
        logger.debug(f"Normalizing document: {url}")
        
        # Extract title from HTML tags if it isn't in metadata
        if not title or title == "Untitled Document":
            title_match = re.search(r'<title>(.*?)<\/title>', raw_content, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()

        # Isolate content within <body> tag to prevent title/metadata leaking into cleaned text
        body_match = re.search(r'<body\b[^>]*>([\s\S]*?)<\/body>', raw_content, re.IGNORECASE)
        content_to_clean = body_match.group(1) if body_match else raw_content

        cleaned_content = cls.clean_html(content_to_clean)
        
        return {
            "url": url,
            "title": title,
            "content": cleaned_content,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }

