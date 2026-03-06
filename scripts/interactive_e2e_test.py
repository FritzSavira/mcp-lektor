"""Interaktiver End-to-End-Test: erzeugt output_test.docx"""

import asyncio
import json
from pathlib import Path

from mcp_lektor.core.document_io import read_document
from mcp_lektor.core.proofreading_engine import ProofreadingEngine
from mcp_lektor.core.document_io import write_corrected_document

# --- Konfiguration ---
INPUT_FILE = Path("tests/fixtures/sample_with_errors.docx")
OUTPUT_FILE = Path("output_test.docx")
AUTHOR = "MCP-Lektor"


async def main():
    # 1. Dokument einlesen
    print("=" * 60)
    print("1. Dokument einlesen …")
    structure = read_document(INPUT_FILE)
    print(f"   ✓ {len(structure.paragraphs)} Absätze gelesen")
    print(f"   ✓ Platzhalter: {structure.placeholder_count}")

    # 2. Korrekturlauf starten
    print("\n2. Korrekturlauf starten …")
    engine = ProofreadingEngine()
    corrections = await engine.proofread(structure, checks="all")
    print(f"   ✓ {len(corrections)} Korrekturen gefunden")

    for i, c in enumerate(corrections, 1):
        print(f"   [{i}] {c.category.value}: "
              f"'{c.original_text}' → '{c.suggested_text}' "
              f"({c.confidence.value})")

    # 3. Korrigiertes Dokument schreiben
    print(f"\n3. Korrigiertes Dokument schreiben → {OUTPUT_FILE}")
    write_corrected_document(
        input_path=INPUT_FILE,
        output_path=OUTPUT_FILE,
        corrections=corrections,
        author=AUTHOR,
    )
    print(f"   ✓ Datei erzeugt: {OUTPUT_FILE.resolve()}")

    # 4. Kurze Verifizierung
    print("\n4. Verifizierung …")
    assert OUTPUT_FILE.exists(), "output_test.docx wurde nicht erstellt!"
    print(f"   ✓ Dateigröße: {OUTPUT_FILE.stat().st_size:,} Bytes")
    print("=" * 60)
    print("FERTIG — bitte output_test.docx in Word/LibreOffice öffnen.")


if __name__ == "__main__":
    asyncio.run(main())
