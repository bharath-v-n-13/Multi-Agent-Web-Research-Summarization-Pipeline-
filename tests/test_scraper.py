from app.search.scraper import Scraper

def test_clean_html_removes_tags():
    """
    Tests HTML tag stripping while preserving text contents.
    """
    html = "<div><p>Hello <b>World</b>!</p></div>"
    cleaned = Scraper.clean_html(html)
    assert cleaned == "Hello World !"

def test_clean_html_removes_scripts_and_styles():
    """
    Tests that scripts and styles are entirely deleted, not just stripped of tags.
    """
    html = """
    <html>
    <head>
        <style>body { color: red; }</style>
        <script>console.log("hello");</script>
        <title>Scraper Test</title>
    </head>
    <body>
        <h1>Content Text</h1>
    </body>
    </html>
    """
    cleaned = Scraper.clean_html(html)
    assert "color: red" not in cleaned
    assert "console.log" not in cleaned
    assert "Content Text" in cleaned

def test_scraper_normalizes_doc():
    """
    Tests full scraping normalization logic.
    """
    raw_doc = {
        "url": "https://test.org/article-1",
        "title": "",
        "content": "<html><head><title>Fall Back Title</title></head><body>Main body text</body></html>"
    }
    
    normalized = Scraper.scrape(raw_doc)
    
    assert normalized["url"] == "https://test.org/article-1"
    assert normalized["title"] == "Fall Back Title"
    assert normalized["content"] == "Main body text"
    assert "timestamp" in normalized
    assert normalized["timestamp"].endswith("Z")
