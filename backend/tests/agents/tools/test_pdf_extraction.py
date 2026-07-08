from aureon.agents.tools.pdf_extraction import MIN_READABLE_CHARS, extract_pdf_text


def _build_minimal_pdf(text: str) -> bytes:
    """Builds a real, valid, minimal single-page PDF with the given text
    embedded in an actual content stream (not a fixture file) — no
    reportlab/extra dependency needed, just correct PDF byte offsets."""
    stream_content = f"BT /F1 12 Tf 10 700 Td ({text}) Tj ET".encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> "
        b"/MediaBox [0 0 612 792] /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream_content)).encode() + b" >>\nstream\n" + stream_content + b"\nendstream",
    ]

    header = b"%PDF-1.4\n"
    body = bytearray()
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(header) + len(body))
        body += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"

    xref_offset = len(header) + len(body)
    xref = f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        xref += f"{offset:010} 00000 n \n".encode()

    trailer = (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode()
    )

    return header + bytes(body) + xref + trailer


def _build_encrypted_pdf() -> bytes:
    """A real PDF, then genuinely encrypted with pypdf itself (not a
    fabricated byte string claiming to be encrypted)."""
    from pypdf import PdfWriter

    plain = _build_minimal_pdf("Confidential")
    import io

    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(plain))
    writer = PdfWriter()
    writer.append_pages_from_reader(reader)
    writer.encrypt(user_password="secret")
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_extracts_real_embedded_text():
    pdf_bytes = _build_minimal_pdf("Education Experience Skills Projects " * 6)

    result = extract_pdf_text(pdf_bytes)

    assert result.status == "completed"
    assert "Education Experience Skills Projects" in result.text
    assert result.page_count == 1


def test_encrypted_pdf_is_never_guessed_at():
    pdf_bytes = _build_encrypted_pdf()

    result = extract_pdf_text(pdf_bytes)

    assert result.status == "encrypted"
    assert result.text == ""


def test_corrupt_bytes_are_invalid_document_not_a_crash():
    result = extract_pdf_text(b"this is not a real PDF file at all")

    assert result.status == "invalid_document"
    assert result.text == ""


def test_near_empty_text_is_no_readable_text():
    # A real PDF whose embedded text is far too short to be usable.
    pdf_bytes = _build_minimal_pdf("Hi")

    result = extract_pdf_text(pdf_bytes)

    assert result.status == "no_readable_text"
    assert len(result.text) < MIN_READABLE_CHARS
