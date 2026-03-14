import streamlit as st
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from datetime import datetime

# Importe korrigiert: Wir importieren die Funktionen und die korrekten Modelle
from mcp_lektor.core.document_io import parse_docx, write_corrected_document
from mcp_lektor.core.proofreading_engine import ProofreadingEngine
from mcp_lektor.core.bible_validator import BibleValidator
from mcp_lektor.core.enums import CorrectionCategory

# Lade Umgebungsvariablen für API-Keys
load_dotenv()

st.set_page_config(
    page_title="MCP-Lektor: Full Auto Mode",
    page_icon="✍️",
    layout="centered"
)

from mcp_lektor.config.settings import get_settings

# Initialisierung der Core-Komponenten
# CACHING DEAKTIVIERT: Damit Änderungen an der config.yaml sofort wirksam werden
def get_engine():
    settings = get_settings(reload=True)
    return ProofreadingEngine(config=settings.proofreading)

@st.cache_resource
def get_bible_validator():
    return BibleValidator()

engine = get_engine()
bible_val = get_bible_validator()

st.title("✍️ MCP-Lektor")
st.markdown("""
### Modus: Full Auto (Direkt-Lektorat)
Lade eine `.docx` Datei hoch. Der Lektor prüft den Text (KI + Regeln) und erstellt **sofort** ein Dokument mit Track Changes und Kommentaren.
""")

# Sidebar für Einstellungen
with st.sidebar:
    st.header("Einstellungen")
    available_cats = [cat.name.lower() for cat in CorrectionCategory]
    categories = st.multiselect(
        "Prüf-Kategorien",
        available_cats,
        default=available_cats
    )
    st.divider()
    if engine.config.smart_llm_selector:
        st.info(f"LLM Selector: {engine.config.smart_llm_selector}")
    else:
        st.info(f"LLM Model: {engine.config.llm_model}")

# Session State Initialisierung
if "processed" not in st.session_state:
    st.session_state.processed = False
if "output_bytes" not in st.session_state:
    st.session_state.output_bytes = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None
if "num_corrections" not in st.session_state:
    st.session_state.num_corrections = 0

# 1. Datei Upload
uploaded_file = st.file_uploader("Wähle eine Word-Datei (.docx)", type="docx")

if uploaded_file and (st.session_state.file_name != uploaded_file.name):
    # Neue Datei geladen - Reset
    st.session_state.file_name = uploaded_file.name
    st.session_state.processed = False
    st.session_state.output_bytes = None
    st.session_state.num_corrections = 0

# 2. Analyse & Export Prozess (Full Auto)
if uploaded_file and not st.session_state.processed:
    if st.button("Lektorat starten"):
        with st.status("Verarbeite Dokument...", expanded=True) as status:
            temp_dir = Path("/tmp")
            temp_dir.mkdir(exist_ok=True)
            temp_input = temp_dir / uploaded_file.name
            temp_output = temp_dir / f"lektoriert_{uploaded_file.name}"
            
            try:
                # A. Lese Dokument
                status.write("Lese Dokumentstruktur...")
                with open(temp_input, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                doc_data = parse_docx(temp_input)
                
                # B. Analyse (Async)
                status.write("Führe Lektorat durch (KI & Regeln)...")
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                engine_cats = [CorrectionCategory[c.upper()] for c in categories]
                result = loop.run_until_complete(engine.proofread(doc_data, checks=engine_cats))
                st.session_state.num_corrections = result.total_corrections
                
                # C. Bibel-Check
                status.write("Prüfe Bibelstellen...")
                # Wir führen Bibelstellen-Checks durch, loggen sie aber nur
                loop.run_until_complete(bible_val.validate(doc_data))
                
                # D. Export (Alle Korrekturen automatisch annehmen)
                status.write("Erstelle Word-Datei mit Track Changes...")
                decisions = {i: "accept" for i in range(len(result.corrections))}
                corrections_list = [c.model_dump() for c in result.corrections]
                
                result_path = write_corrected_document(
                    input_path=temp_input,
                    output_path=temp_output,
                    corrections=corrections_list,
                    author="MCP-Lektor-Auto",
                    decisions=decisions
                )
                
                with open(result_path, "rb") as f:
                    st.session_state.output_bytes = f.read()
                
                st.session_state.processed = True
                status.update(label="Lektorat abgeschlossen!", state="complete", expanded=False)
                
            except Exception as e:
                st.error(f"Fehler bei der Verarbeitung: {str(e)}")
                status.update(label="Verarbeitung fehlgeschlagen.", state="error")
            finally:
                if temp_input.exists(): os.remove(temp_input)
                if temp_output.exists(): os.remove(temp_output)
        
        st.rerun()

# 3. Download Bereich
if st.session_state.processed and st.session_state.output_bytes:
    st.divider()
    st.balloons()
    st.success(f"Fertig! Es wurden **{st.session_state.num_corrections}** Korrekturen gefunden und als Track Changes eingearbeitet.")
    
    # Zeitstempel für eindeutigen Dateinamen generieren
    timestamp = datetime.now().strftime("%H-%M-%S")
    
    st.download_button(
        label="📥 Korrigiertes Dokument herunterladen",
        data=st.session_state.output_bytes,
        file_name=f"lektoriert_{st.session_state.file_name.replace('.docx', '')}_{timestamp}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )
    
    if st.button("Anderes Dokument prüfen"):
        st.session_state.processed = False
        st.session_state.file_name = None
        st.rerun()
