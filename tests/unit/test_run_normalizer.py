"""Unit tests for the RunNormalizer."""

import pytest
from mcp_lektor.core.models import RunFormatting, TextRun, TextColor
from mcp_lektor.core.run_normalizer import normalize_runs

def test_merge_identical_runs():
    fmt = RunFormatting(bold=True, font_name="Arial")
    runs = [
        TextRun(text="Hello ", formatting=fmt),
        TextRun(text="World", formatting=fmt),
    ]
    
    normalized = normalize_runs(runs)
    assert len(normalized) == 1
    assert normalized[0].text == "Hello World"
    assert normalized[0].formatting.bold is True

def test_keep_different_formatting_separate():
    fmt1 = RunFormatting(bold=True)
    fmt2 = RunFormatting(bold=False)
    runs = [
        TextRun(text="Bold", formatting=fmt1),
        TextRun(text="Plain", formatting=fmt2),
    ]
    
    normalized = normalize_runs(runs)
    assert len(normalized) == 2
    assert normalized[0].text == "Bold"
    assert normalized[1].text == "Plain"

def test_placeholder_differentiation():
    fmt = RunFormatting(color=TextColor(r=255, g=0, b=0))
    # Both have same formatting (red), but one is marked placeholder
    runs = [
        TextRun(text="Normal Red", formatting=fmt, is_placeholder=False),
        TextRun(text="[Placeholder]", formatting=fmt, is_placeholder=True),
    ]
    
    normalized = normalize_runs(runs)
    assert len(normalized) == 2

def test_merge_multiple_runs():
    fmt = RunFormatting(italic=True)
    runs = [
        TextRun(text="One", formatting=fmt),
        TextRun(text="Two", formatting=fmt),
        TextRun(text="Three", formatting=fmt),
    ]
    
    normalized = normalize_runs(runs)
    assert len(normalized) == 1
    assert normalized[0].text == "OneTwoThree"

def test_empty_runs():
    assert normalize_runs([]) == []
