import asyncio
import base64
import json
import os
from pathlib import Path
from docx import Document
from mcp_lektor.tools.extract_document import extract_document
from mcp_lektor.tools.write_corrected_docx import write_corrected_docx
from mcp_lektor.core.session_manager import session_manager
from mcp_lektor.core.models import ProofreadingResult, ProposedCorrection
from mcp_lektor.core.enums import CorrectionCategory, ConfidenceLevel

async def test():
    # 1. Create dummy docx
    doc = Document()
    doc.add_paragraph("Hello World")
    doc_path = Path("test_upload.docx")
    doc.save(doc_path)
    
    try:
        # 2. Encode
        content = base64.b64encode(doc_path.read_bytes()).decode()
        
        # 3. Call extract_document
        print("Calling extract_document...")
        result_json = await extract_document(file_content=content, filename="test_upload.docx")
        result = json.loads(result_json)
        
        if "error" in result:
            print(f"Error: {result['error']}")
            return

        session_id = result["session_id"]
        print(f"Session ID: {session_id}")
        
        # 4. Mock proofreading result
        session = session_manager.get_session(session_id)
        
        # Paragraph 0: "Hello World" -> "Hello Planet"
        correction = ProposedCorrection(
            id="C-001",
            paragraph_index=0,
            run_index=0, # Assuming "Hello World" is in one run
            char_offset_start=6,
            char_offset_end=11,
            original_text="World",
            suggested_text="Planet",
            category=CorrectionCategory.SPELLING,
            confidence=ConfidenceLevel.HIGH,
            explanation="Testing correction"
        )
        
        proof_result = ProofreadingResult(
            document_filename="test_upload.docx",
            corrections=[correction]
        )
        
        session_manager.update_session(session_id, {"proofreading_result": proof_result})
        
        # 5. Call write_corrected_docx
        print("Calling write_corrected_docx...")
        write_result_json = await write_corrected_docx(session_id=session_id, apply_all=True)
        write_result = json.loads(write_result_json)
        
        if "error" in write_result:
            print(f"Error in write: {write_result['error']}")
            return
            
        if "file_content" not in write_result:
            print("FAILED: No file_content in response")
            return
            
        print("Received file_content (Base64).")
        
        # Verify it decodes
        try:
            decoded = base64.b64decode(write_result["file_content"])
            if len(decoded) > 0:
                print("Base64 decoded successfully.")
            else:
                print("FAILED: Base64 decoded to empty bytes.")
        except Exception as e:
            print(f"FAILED: Base64 decode error: {e}")

        # 6. Check session cleanup
        session = session_manager.get_session(session_id)
        temp_files = session.get("temp_files", [])
        print(f"Temp files tracked: {len(temp_files)}")
        
        # 7. Delete session
        session_manager.delete_session(session_id)
        
        # Check if files are gone
        all_deleted = True
        for f in temp_files:
            if Path(f).exists():
                print(f"FAILED: Temp file {f} was not deleted.")
                all_deleted = False
            else:
                print(f"SUCCESS: Temp file {Path(f).name} was deleted.")
        
        if all_deleted:
            print("All temp files cleaned up.")

    finally:
        if doc_path.exists():
            doc_path.unlink()

if __name__ == "__main__":
    asyncio.run(test())
