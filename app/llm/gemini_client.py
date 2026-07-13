import os
import json
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from groq import AsyncGroq
from app.utils.config import settings
from app.utils.logger import logger

T = TypeVar("T", bound=BaseModel)

class GeminiClient:
    """
    A transparent drop-in wrapper around the official groq SDK that acts as GeminiClient.
    This avoids changing import paths in other parts of the application.
    """
    def __init__(self, api_key: Optional[str] = None):
        key = api_key or settings.groq_api_key
        if not key:
            key = os.environ.get("GROQ_API_KEY", "")
            
        if not key:
            logger.warning("GROQ_API_KEY is not defined. Calls to Groq endpoints will fail.")
            
        self.client = AsyncGroq(api_key=key)
        self.model = settings.groq_model

    async def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Asynchronously generates freeform text using Groq.
        """
        logger.debug(f"Generating text using Groq model '{self.model}'...")
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Groq text generation failed: {e}")
            raise Exception(f"Groq API failure: {str(e)}") from e

    async def generate_structured(
        self, 
        prompt: str, 
        response_schema: Type[T], 
        system_instruction: Optional[str] = None
    ) -> T:
        """
        Asynchronously generates structured JSON content conforming to the provided Pydantic model.
        """
        logger.debug(f"Generating structured JSON using Groq model '{self.model}'...")
        
        # Guide the model to follow the specific Pydantic JSON schema
        schema_json = json.dumps(response_schema.model_json_schema())
        system_content = (
            "You are a helpful assistant. You must respond ONLY with a raw JSON object conforming strictly to this JSON Schema:\n"
            f"{schema_json}\n"
            "Do not include any wrapping markdown blocks (e.g. ```json), explanation text, or extra spacing outside the JSON object."
        )
        
        if system_instruction:
            system_content = f"{system_instruction}\n\n{system_content}"

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            raw_text = response.choices[0].message.content or ""
            # Validate raw JSON using Pydantic
            validated_output = response_schema.model_validate_json(raw_text)
            return validated_output
        except Exception as e:
            logger.error(f"Groq structured generation failed: {e}")
            raise Exception(f"Groq API failure during structured parsing: {str(e)}") from e
