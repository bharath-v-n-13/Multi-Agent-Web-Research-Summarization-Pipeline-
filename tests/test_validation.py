import pytest
from pydantic import ValidationError
from app.models.request import ResearchRequest

def test_valid_request():
    """
    Tests request validation with fully valid parameters.
    """
    req = ResearchRequest(
        topic="Future of Quantum Computing",
        depth="deep",
        max_sources=25,
        output_format="pdf"
    )
    assert req.topic == "Future of Quantum Computing"
    assert req.depth == "deep"
    assert req.max_sources == 25
    assert req.output_format == "pdf"

def test_default_values():
    """
    Tests defaults are applied correctly.
    """
    req = ResearchRequest(topic="Artificial Intelligence Trends")
    assert req.depth == "moderate"
    assert req.max_sources == 20
    assert req.output_format == "markdown"

def test_invalid_topic_length():
    """
    Topic must be between 5 and 200 characters.
    """
    # Too short
    with pytest.raises(ValidationError):
        ResearchRequest(topic="AI")
    
    # Too long
    with pytest.raises(ValidationError):
        ResearchRequest(topic="A" * 201)

def test_invalid_depth():
    """
    Depth must be one of: shallow, moderate, deep.
    """
    with pytest.raises(ValidationError):
        ResearchRequest(topic="Valid Topic", depth="super-deep")

def test_invalid_max_sources_range():
    """
    max_sources must be between 5 and 50.
    """
    # Too low
    with pytest.raises(ValidationError):
        ResearchRequest(topic="Valid Topic", max_sources=4)
        
    # Too high
    with pytest.raises(ValidationError):
        ResearchRequest(topic="Valid Topic", max_sources=51)

def test_invalid_format():
    """
    output_format must be one of: markdown, pdf, json.
    """
    with pytest.raises(ValidationError):
        ResearchRequest(topic="Valid Topic", output_format="docx")
