# MCP Lektor: Projekt-Evolution & Meilensteine

Dieses Dokument hält die strategischen Entscheidungen und architektonischen Änderungen während der Entwicklung fest.

## [v0.2] - 2026-03-07: Full Auto Mode (Phase 3 Entfernung)

### Strategische Entscheidung
Die interaktive Review-Phase ("Phase 3") wird aus dem Workflow entfernt. Der MCP-Lektor arbeitet nun als direkter Automat: Input (.docx) -> Analyse -> Output (.docx mit Track Changes).

**Begründung:** 
- Maximale Effizienz für den Benutzer.
- Fokus auf "Track Changes" als primäres Feedback-Medium (Benutzer prüft direkt in Word).
- Reduzierung der Komplexität in der GUI.

### Technische Umsetzung
- `gui.py` wurde so modifiziert, dass nach der Analyse sofort die `write_corrected_document` Funktion mit `decisions = {all: "accept"}` aufgerufen wird.
- Die Review-Tabelle wurde entfernt.

### Status & Tests
- [ ] Integrationstest mit Straico v.0 API.
- [ ] Validierung der Track Changes im Output.
- [ ] Performance-Check bei großen Dokumenten.

---

## [v0.1] - 2026-03-06: Initial Prototype
- Grundlegende MCP-Server-Struktur.
- Straico API Integration (v1).
- Streamlit GUI mit Review-Tabelle.
- OpenXML Writer mit Track Changes Support.
