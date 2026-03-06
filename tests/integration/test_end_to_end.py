"""End-to-end integration tests for the full proofreading pipeline."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock

from mcp_lektor.core.session_manager import session_manager
from mcp_lektor.tools.extract_document import extract_document
from mcp_lektor.tools.proofread_text import proofread_text
from mcp_lektor.tools.validate_bible_refs import validate_bible_refs
from mcp_lektor.tools.write_corrected_docx import write_corrected_docx

@pytest.fixture(autouse=True)
def _clean_sessions():
    session_manager._sessions.clear()
    yield
    session_manager._sessions.clear()

@pytest.mark.asyncio
async def test_full_pipeline_rule_based(sample_docx_path: Path):
    """
    Test the full pipeline using rule-based checks.
    This doesn't require a real LLM API key.
    """
    # 1. Extract
    extract_res_raw = await extract_document(str(sample_docx_path))
    extract_res = json.loads(extract_res_raw)
    assert "session_id" in extract_res
    session_id = extract_res["session_id"]
    
    # 2. Proofread (Rule-based only to avoid API calls)
    # Typography, Quotation, Confused words
    proof_res_raw = await proofread_text(session_id, checks="typography,quotation,confused")
    proof_res = json.loads(proof_res_raw)
    assert "corrections" in proof_res
    
    # 3. Bible Validation
    bible_res_raw = await validate_bible_refs(session_id)
    bible_res = json.loads(bible_res_raw)
    assert "results" in bible_res

    # 4. Write
    write_res_raw = await write_corrected_docx(session_id, apply_all=True)
    write_res = json.loads(write_res_raw)
    
    assert "status" in write_res
    assert write_res["status"] == "success"
    
    # If no corrections were found, there's no output path, which is fine
    if "output_path" in write_res:
        assert Path(write_res["output_path"]).exists()
    else:
        assert "nothing to write" in write_res["message"].lower()

@pytest.mark.asyncio
async def test_full_pipeline_with_mocked_llm(sample_docx_path: Path):
    """
    Test the full pipeline including LLM-based checks by mocking the API call.
    """
    # Mock the LLM client call
    mock_corrections = [
        {
            "paragraph_index": 1,
            "run_index": 0,
            "char_offset_start": 0,
            "char_offset_end": 4,
            "original_text": "Dies",
            "suggested_text": "DAS",
            "category": "Rechtschreibung",
            "confidence": "high",
            "explanation": "Test correction"
        }
    ]
    
    with patch("mcp_lektor.core.llm_client.call_llm_for_proofreading", new_callable=AsyncMock) as mock_call:
        mock_call.return_value = mock_corrections
        
        # 1. Extract
        extract_res_raw = await extract_document(str(sample_docx_path))
        session_id = json.loads(extract_res_raw)["session_id"]
        
        # 2. Proofread (including spelling to trigger LLM)
        proof_res_raw = await proofread_text(session_id, checks="spelling")
        proof_res = json.loads(proof_res_raw)
        
        assert proof_res["total_corrections"] > 0
        
        # 3. Write
        write_res_raw = await write_corrected_docx(session_id, apply_all=True)
        write_res = json.loads(write_res_raw)
        
        assert write_res.get("status") == "success", f"Error: {write_res.get('error')}"
        assert write_res["corrections_applied"] > 0
        assert "output_path" in write_res
        assert Path(write_res["output_path"]).exists()
