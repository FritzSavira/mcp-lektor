# DEV_TASKS-0001 – Part 4: Bible Reference Validator

## Überblick

Part 4 implementiert die Bibelstellen-Erkennung und -Validierung:
- `src/mcp_lektor/utils/bible_patterns.py` – Regex-Muster für deutsche Bibelreferenzen
- `src/mcp_lektor/core/bible_validator.py` – Extraktion + Online/Offline-Validierung
- `src/mcp_lektor/tools/validate_bible_refs.py` – MCP-Tool-Wrapper
- `tests/unit/test_bible_validator.py` – Unit-Tests

## Aufgaben

### Task 4.1: bible_patterns.py anlegen
- [ ] Datei `src/mcp_lektor/utils/bible_patterns.py` aus dem ZIP übernehmen
- [ ] Inhalt: `BIBLE_REF_PATTERN` (compiled regex) + `extract_references()` Hilfsfunktion
- [ ] Deckt ab: AT + NT Abkürzungen, nummerierte Bücher (1. Mose, 2. Kor …), Kapitel, Vers, Vers-Bereiche mit `-` oder `–`

### Task 4.2: bible_validator.py anlegen
- [ ] Datei `src/mcp_lektor/core/bible_validator.py` aus dem ZIP übernehmen
- [ ] `BibleValidator` Klasse mit `extract_refs()` und `validate()`
- [ ] Offline-Fallback: `_FALLBACK_CHAPTER_COUNTS` Dict prüft Kapitelnummern
- [ ] Online-Validierung via `httpx.AsyncClient` gegen `bible-api.com`
- [ ] Graceful Degradation: bei API-Fehler → Offline-Fallback + Warnung

### Task 4.3: validate_bible_refs.py Tool anlegen
- [ ] Datei `src/mcp_lektor/tools/validate_bible_refs.py` aus dem ZIP übernehmen
- [ ] Liest `DocumentStructure` aus der Session
- [ ] Speichert `bible_validation_results` zurück in die Session
- [ ] Gibt JSON mit Zusammenfassung + Einzelergebnissen zurück

### Task 4.4: Unit-Tests anlegen und ausführen
- [ ] Datei `tests/unit/test_bible_validator.py` aus dem ZIP übernehmen
- [ ] Tests ausführen: `pytest tests/unit/test_bible_validator.py -v`
- [ ] Erwartung: alle Tests grün

### Task 4.5: Interaktiver Check
- [ ] Im Python-REPL oder einem kleinen Skript testen:
  ```python
  from mcp_lektor.utils.bible_patterns import extract_references
  refs = extract_references("Siehe Mt 5,3-12 und 1. Mose 1,1 sowie Offb 22,21.")
  for r in refs:
      print(r)
  ```
- [ ] Erwartung: 3 Referenzen erkannt (Mt, 1. Mose, Offb)

## Acceptance Criteria
- [ ] `pytest tests/unit/test_bible_validator.py -v` → alle Tests grün
- [ ] Regex erkennt: einfache Refs (Mt 5,3), Bereiche (1. Kor 13,4-7), Kapitel-only (Ps 23), Doppelpunkt-Syntax (Joh 3:16)
- [ ] Offline-Validierung erkennt ungültige Kapitel (Gen 99) und unbekannte Bücher
- [ ] Placeholder-Absätze werden übersprungen
- [ ] Kein bestehender Test bricht (auch `test_proofreading_engine.py` weiterhin grün)
