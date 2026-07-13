from typing import Literal
from pydantic import BaseModel, Field

class ResearchRequest(BaseModel):
    """
    Validates requests submitted to the /research endpoint.
    Enforces strict typing and constraints in compliance with Pydantic V2.
    """
    topic: str = Field(
        ..., 
        min_length=5, 
        max_length=200, 
        description="The target topic to perform research on."
    )
    depth: Literal["shallow", "moderate", "deep"] = Field(
        default="moderate",
        description="The depth of research: 'shallow' (breadth-first), 'moderate' (balanced), 'deep' (iterative-deepening)."
    )
    max_sources: int = Field(
        default=20, 
        ge=5, 
        le=50, 
        description="The maximum number of unique sources to crawl and search over."
    )
    output_format: Literal["markdown", "pdf", "json"] = Field(
        default="markdown",
        description="The requested output format of the report."
    )
