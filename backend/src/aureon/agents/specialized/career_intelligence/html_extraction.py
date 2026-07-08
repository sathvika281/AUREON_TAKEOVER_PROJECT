import re
from html.parser import HTMLParser

#: Tags whose contents are never real page content — navigation chrome,
#: scripts/styles, etc. Everything inside these is dropped entirely.
_SKIP_TAGS = frozenset({"script", "style", "nav", "header", "footer", "noscript", "svg"})

#: Keeps the LLM prompt this feeds into bounded — a real webpage can be
#: hundreds of KB; only a representative slice is needed for extraction.
MAX_EXTRACTED_CHARS = 8000


class _ReadableTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in _SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in _SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0 and data.strip():
            self._chunks.append(data.strip())

    def text(self) -> str:
        return " ".join(self._chunks)


def extract_readable_text(html: str) -> str:
    """Real HTML-to-text extraction, stdlib only (no BeautifulSoup/lxml
    needed) — strips script/style/nav/header/footer content and returns
    the remaining visible text, whitespace-collapsed and bounded. This is
    the deterministic "facts" layer: real text pulled from a real page,
    never summarized or interpreted here — that's the LLM's job
    (url_investigation.py), working only from what this function actually
    found."""
    parser = _ReadableTextExtractor()
    parser.feed(html)
    text = re.sub(r"\s+", " ", parser.text()).strip()
    return text[:MAX_EXTRACTED_CHARS]
