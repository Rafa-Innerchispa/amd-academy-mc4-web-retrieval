import re
from html.parser import HTMLParser
from typing import List, Dict

class _SimpleHTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.links = []
        self.tables = []
        self._current_table = []
        self._current_row = []
        self._current_cell = []
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._cell_is_header = False
        self._skip_depth = 0
        self.skip_tags = {"script", "style", "nav", "footer", "header", "aside", "svg", "noscript", "iframe"}

    def handle_starttag(self, tag, attrs):
        lower_tag = tag.lower()
        if lower_tag in self.skip_tags:
            self._skip_depth += 1
            return
        if self._skip_depth > 0:
            return

        if lower_tag == "a":
            for k, v in attrs:
                if k.lower() == "href" and v:
                    v_strip = v.strip()
                    if v_strip and not v_strip.startswith(("#", "javascript:", "mailto:", "tel:")):
                        self.links.append(v_strip)

        elif lower_tag == "table":
            self._in_table = True
            self._current_table = []
        elif lower_tag == "tr" and self._in_table:
            self._in_row = True
            self._current_row = []
        elif lower_tag in ("td", "th") and self._in_row:
            self._in_cell = True
            self._current_cell = []
            self._cell_is_header = (lower_tag == "th")

    def handle_endtag(self, tag):
        lower_tag = tag.lower()
        if lower_tag in self.skip_tags:
            if self._skip_depth > 0:
                self._skip_depth -= 1
            return
        if self._skip_depth > 0:
            return

        if lower_tag in ("td", "th") and self._in_cell:
            cell_text = "".join(self._current_cell).strip()
            self._current_row.append((self._cell_is_header, cell_text))
            self._in_cell = False
        elif lower_tag == "tr" and self._in_row:
            if self._current_row:
                self._current_table.append(self._current_row)
            self._in_row = False
        elif lower_tag == "table" and self._in_table:
            if self._current_table:
                # Convert table rows to list of dicts if first row looks like headers
                headers = [txt for is_h, txt in self._current_table[0]]
                formatted_rows = []
                for row in self._current_table[1:]:
                    cells = [txt for is_h, txt in row]
                    if len(cells) == len(headers):
                        formatted_rows.append(dict(zip(headers, cells)))
                if formatted_rows:
                    self.tables.append(formatted_rows)
            self._in_table = False

    def handle_data(self, data):
        if self._skip_depth > 0:
            return
        cleaned = data.strip()
        if cleaned:
            self.text_parts.append(cleaned)
            if self._in_cell:
                self._current_cell.append(data)


class DOMExtractor:
    """
    Boilerplate stripper and structured markdown / table content extractor.
    Runs with zero external dependencies via Python standard library html.parser,
    and upgrades to BeautifulSoup when installed.
    """

    def extract_clean_text(self, html_content: str) -> str:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            for tag in ["script", "style", "nav", "footer", "header", "aside", "svg", "noscript", "iframe"]:
                for el in soup.find_all(tag):
                    el.decompose()
            text = soup.get_text(separator=" ", strip=True)
            return re.sub(r'\s+', ' ', text)
        except ImportError:
            parser = _SimpleHTMLTextExtractor()
            parser.feed(html_content)
            return " ".join(parser.text_parts)

    def extract_links(self, html_content: str) -> List[str]:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            links = []
            for a in soup.find_all("a", href=True):
                href = a["href"].strip()
                if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    links.append(href)
            return list(dict.fromkeys(links))
        except ImportError:
            parser = _SimpleHTMLTextExtractor()
            parser.feed(html_content)
            return list(dict.fromkeys(parser.links))

    def extract_tables(self, html_content: str) -> List[List[Dict[str, str]]]:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, "html.parser")
            tables_data = []
            for table in soup.find_all("table"):
                headers = []
                header_row = table.find("tr")
                if not header_row:
                    continue
                for th in header_row.find_all(["th", "td"]):
                    headers.append(th.get_text(strip=True))
                if not headers:
                    continue
                rows = []
                for tr in table.find_all("tr")[1:]:
                    cells = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
                    if len(cells) == len(headers):
                        rows.append(dict(zip(headers, cells)))
                if rows:
                    tables_data.append(rows)
            return tables_data
        except ImportError:
            parser = _SimpleHTMLTextExtractor()
            parser.feed(html_content)
            return parser.tables
