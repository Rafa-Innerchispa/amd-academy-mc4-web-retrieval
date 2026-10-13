from src.extractor.dom_extractor import DOMExtractor

def test_dom_extractor_strips_boilerplate_and_extracts_clean_text():
    html = """
    <html>
        <head><title>Test Page</title></head>
        <script>alert('bad');</script>
        <style>body { color: red; }</style>
        <nav><a href="/home">Home</a></nav>
        <body>
            <h1>AMD ROCm Platform</h1>
            <p>ROCm 6.2 was officially released on July 2024.</p>
        </body>
        <footer>Copyright 2026</footer>
    </html>
    """
    extractor = DOMExtractor()
    clean = extractor.extract_clean_text(html)

    assert "AMD ROCm Platform" in clean
    assert "ROCm 6.2 was officially released on July 2024." in clean
    assert "alert('bad')" not in clean
    assert "Copyright" not in clean

def test_dom_extractor_tables():
    html = """
    <table>
        <tr><th>Accelerator</th><th>Memory</th></tr>
        <tr><td>MI300X</td><td>192GB HBM3</td></tr>
        <tr><td>MI300A</td><td>128GB HBM3</td></tr>
    </table>
    """
    extractor = DOMExtractor()
    tables = extractor.extract_tables(html)

    assert len(tables) == 1
    assert len(tables[0]) == 2
    assert tables[0][0]["Accelerator"] == "MI300X"
    assert tables[0][0]["Memory"] == "192GB HBM3"
