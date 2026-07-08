from aureon.agents.specialized.career_intelligence.html_extraction import (
    MAX_EXTRACTED_CHARS,
    extract_readable_text,
)

SAMPLE_HTML = """
<html>
<head><style>.a { color: red; }</style><script>console.log('x');</script></head>
<body>
<nav>Home | About | Contact</nav>
<header>Site Header</header>
<main>
  <h1>AI Research Careers</h1>
  <p>AI researchers design and evaluate machine learning models.</p>
</main>
<footer>Copyright 2026</footer>
</body>
</html>
"""


def test_strips_script_style_nav_header_footer():
    text = extract_readable_text(SAMPLE_HTML)

    assert "console.log" not in text
    assert "color: red" not in text
    assert "Home | About | Contact" not in text
    assert "Site Header" not in text
    assert "Copyright 2026" not in text
    assert "AI Research Careers" in text
    assert "AI researchers design and evaluate machine learning models." in text


def test_collapses_whitespace():
    text = extract_readable_text("<p>hello    \n\n   world</p>")
    assert text == "hello world"


def test_bounds_length():
    huge_html = "<p>" + ("word " * 5000) + "</p>"
    text = extract_readable_text(huge_html)
    assert len(text) <= MAX_EXTRACTED_CHARS
