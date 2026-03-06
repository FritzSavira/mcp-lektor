import pytest
from mcp_lektor.core.models import DocumentStructure, ProofreadingResult
from mcp_lektor.config.settings import load_config

def test_project_imports():
    """Verify that core modules can be imported without errors."""
    import mcp_lektor
    assert mcp_lektor is not None

def test_models_importable():
    """Verify that pydantic models are functioning."""
    structure = DocumentStructure(
        filename="test.docx",
        paragraphs=[],
        total_paragraphs=0,
        total_words=0,
        placeholder_count=0,
        placeholder_locations=[]
    )
    assert structure.filename == "test.docx"

def test_config_loading(tmp_path):
    """Verify that the config loader exists (even if it might need a real file)."""
    # This is just to check if the function is defined and importable
    from mcp_lektor.config.settings import load_config
    assert callable(load_config)
