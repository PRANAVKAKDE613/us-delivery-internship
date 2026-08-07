import pytest
from src.tam_summariser import generate_account_brief, TAMAccountBrief, TAMSummariserEngine

def test_tam_account_brief_valid():
    brief = generate_account_brief("ACC-001")
    assert isinstance(brief, TAMAccountBrief)
    assert brief.account_id == "ACC-001"
    assert brief.company_name != ""
    assert "### 1. Executive Summary" in brief.formatted_markdown_brief
    assert "### 2. Open Risks & Flagged Issues" in brief.formatted_markdown_brief
    assert "### 3. Recommended Talking Points for TAM" in brief.formatted_markdown_brief

def test_tam_account_brief_executive_summary_length():
    brief = generate_account_brief("ACC-002")
    # Sentences end with '.'
    sentences = [s.strip() for s in brief.executive_summary.split(".") if s.strip()]
    assert 3 <= len(sentences) <= 5

def test_tam_account_brief_determinism():
    brief1 = generate_account_brief("ACC-003").formatted_markdown_brief
    brief2 = generate_account_brief("ACC-003").formatted_markdown_brief
    brief3 = generate_account_brief("ACC-003").formatted_markdown_brief
    assert brief1 == brief2 == brief3

def test_tam_account_brief_invalid_account():
    with pytest.raises(ValueError):
        generate_account_brief("ACC-99999")

def test_tam_streaming():
    engine = TAMSummariserEngine()
    stream_output = "".join(list(engine.stream_brief("ACC-001")))
    brief = generate_account_brief("ACC-001")
    assert stream_output.strip() == brief.formatted_markdown_brief.strip()
