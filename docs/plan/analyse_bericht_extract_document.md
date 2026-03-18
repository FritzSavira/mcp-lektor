# Analysebericht: Fehlerursache beim Aufruf von "Extract Document" in Langdock

## 1. Zusammenfassung (Executive Summary)

Die Fehlermeldung *"It seems the Extract Document tool is looking for files in /app/ which doesn't exist in this environment"* rührt daher, dass der Langdock-Agent versucht, das Dokument über einen **lokalen Dateipfad (`file_path`)** an den MCP-Server zu übergeben. Da der MCP-Server jedoch in einer isolierten Umgebung (z. B. einem Docker-Container oder einem Remote-Server) läuft, hat er keinen Zugriff auf das Dateisystem von Langdock. Der Server löst daraufhin einen `FileNotFoundError` aus, den der Agent (das LLM) für den Nutzer interpretiert und dabei fälschlicherweise annimmt, das Verzeichnis `/app/` sei das Problem.

**Ursache:**
- **Konfigurationsproblem:** Der System-Prompt des Agenten (`AGENT_SYSTEM_PROMPT.md`) weist den Agenten nicht explizit an, den **Base64-Inhalt (`file_content`)** des Dokuments zu nutzen.
- **Agenten-Halluzination:** Das LLM "errät" einen Pfad (oder nutzt einen von Langdock intern bereitgestellten Pfad wie `/app/data/uploads/...`), der auf dem Remote-Server nicht existiert.

---

## 2. Evidenzbasierte Analyse

### 2.1. Code-Fähigkeiten (The "How")
Die Analyse der Datei `src/mcp_lektor/tools/extract_document.py` zeigt, dass das Tool bereits für den Cloud-Einsatz vorbereitet ist. Es unterstützt zwei Modi:
1.  **Lokaler Modus (`file_path`):** Sucht eine Datei auf der Festplatte des Servers.
2.  **Cloud-Modus (`file_content`):** Nimmt einen Base64-kodierten String entgegen, speichert diesen temporär in `/tmp/mcp_lektor/` und verarbeitet ihn dann.

Das Tool wurde laut `CHANGELOG.md` und `DEV_SPEC-0008` genau für diesen Zweck (stateless file transfer in Langdock) implementiert.

### 2.2. Fehler-Rekonstruktion (The "Why")
Wenn ein Nutzer in Langdock eine Datei hochlädt, sieht der Agent diese in seinem Kontext. Ohne genaue Anweisung wählt der Agent den Parameter `file_path`, da dieser in der Tool-Signatur an erster Stelle steht.
- Der Agent ruft auf: `extract_document(file_path="beispiel.docx")`.
- Der Server (im Docker-Container mit Arbeitsverzeichnis `/app`) macht daraus: `/app/beispiel.docx`.
- Die Datei existiert dort nicht -> `FileNotFoundError: File not found: /app/beispiel.docx`.
- Der Server gibt dieses JSON zurück: `{"error": "File not found: /app/beispiel.docx"}`.
- Der Agent liest diesen Fehler und sagt dem Nutzer: *"Es scheint, als würde das Tool in /app/ suchen, was in dieser Umgebung nicht existiert."*

### 2.3. Überprüfung der Hypothesen
- **A) Konfigurationsproblem?** Ja. Der System-Prompt (`docs/agent/AGENT_SYSTEM_PROMPT.md`) ist zu vage. Er sagt: *"rufst du `extract_document` auf"*, ohne zu spezifizieren, dass der Datei-Inhalt (Base64) gesendet werden muss.
- **B) Bug im Code?** Nein. Die Funktion ist vorhanden und in `scripts/test_base64_upload.py` erfolgreich getestet.
- **C) Abweichende Version?** Unwahrscheinlich. Die vorliegende Codebase enthält bereits alle notwendigen Funktionen für die Langdock-Integration.

---

## 3. Empfohlene Maßnahmen

### 3.1. Aktualisierung des Agenten-System-Prompts (Sofortmaßnahme)
Der Prompt in `docs/agent/AGENT_SYSTEM_PROMPT.md` muss präzisiert werden, um dem Agenten mitzuteilen, dass er bei Dokument-Uploads zwingend den Datei-Inhalt als Base64 übertragen muss.

### 3.2. Verbesserung der Tool-Dokumentation
Die Docstrings in `src/mcp_lektor/tools/extract_document.py` sollten so angepasst werden, dass `file_content` als bevorzugter Weg für Cloud-Integrationen hervorgehoben wird.

### 3.3. Test-Absicherung
Es sollte ein automatisierter Integrationstest für den Base64-Pfad in `tests/integration/test_extract_document.py` hinzugefügt werden, um sicherzustellen, dass dieser Pfad in zukünftigen Versionen nicht bricht.

---

## 4. Fazit
Der Code ist korrekt und "cloud-ready". Das Problem liegt in der Kommunikation zwischen dem Agenten und dem Tool. Durch eine Anpassung des System-Prompts wird der Agent angewiesen, die Datei "stateless" (via Base64) zu übertragen, was den Fehler behebt.
