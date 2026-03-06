# DEV_TASKS Part 5 — OpenXML Writer (`write_corrected_docx`)

**Related:** DEV_TECH_DESIGN-0001 Section 4.2, DEV_SPEC-0001 FR-08/FR-09

---

## Ziel

Track Changes (`<w:del>`/`<w:ins>`) und Word-Kommentare in das
Originaldokument schreiben, sodass der Benutzer Korrekturen in
Word/LibreOffice prüfen und annehmen/ablehnen kann.

---

## Dateien

| Datei | Aktion |
|---|---|
| `src/mcp_lektor/core/openxml_writer.py` | **Neu** – Track Changes & Comments |
| `src/mcp_lektor/core/document_io.py` | **Erweitert** – `write_corrected_document()` |
| `src/mcp_lektor/tools/write_corrected_docx.py` | **Neu** – MCP-Tool |
| `tests/unit/test_openxml_writer.py` | **Neu** – Unit-Tests |
| `tests/integration/test_write_corrected_docx.py` | **Neu** – Integrationstests |

---

## Schritte

### Step 5.1: OpenXML Writer implementieren
- [ ] `openxml_writer.py` gemäß Tech Design anlegen
- [ ] `black .` und `ruff check .`
- [ ] Unit-Tests ausführen: `pytest tests/unit/test_openxml_writer.py -v`

### Step 5.2: Document write-back in document_io.py
- [ ] `write_corrected_document()` zur bestehenden `document_io.py` hinzufügen
- [ ] `black .` und `ruff check .`

### Step 5.3: MCP-Tool write_corrected_docx
- [ ] Tool-Stub ersetzen
- [ ] Integrationstests: `pytest tests/integration/test_write_corrected_docx.py -v`

### Step 5.4: Interaktiver Test
- [ ] Testskript ausführen:
```python
from docx import Document as DocxDocument
from mcp_lektor.core.openxml_writer import apply_corrections_to_document, _save_comments_part

doc = DocxDocument()
doc.add_paragraph("Dies ist ein Testtext mit einem Fehler.")

corrections = [{
    "paragraph_index": 0,
    "run_index": 0,
    "char_start": 31,
    "char_end": 37,
    "original_text": "Fehler",
    "replacement_text": "Erfolg",
    "category": "Rechtschreibung",
    "explanation": "Testkorrektur",
}]

apply_corrections_to_document(doc, corrections)
_save_comments_part(doc)
doc.save("output_test.docx")
print("Gespeichert als output_test.docx — bitte in Word öffnen!")
