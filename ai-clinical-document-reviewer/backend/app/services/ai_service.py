import json
import re
from typing import Dict, Any, Optional
import httpx
from pydantic import ValidationError
from app.config import settings
from app.prompts.clinical_review_prompt import (
    CLINICAL_REVIEW_SYSTEM_PROMPT,
    build_clinical_review_prompt,
)
from app.schemas.report import StructuredClinicalReport
from app.utils.logger import logger


class AIAnalysisError(Exception):
    """Base exception for AI analysis errors."""
    def __init__(self, message: str, code: str = "AI_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AIServiceUnavailableError(AIAnalysisError):
    def __init__(self, message: str = "The AI analysis service is temporarily unavailable. Please try again."):
        super().__init__(message, code="AI_SERVICE_UNAVAILABLE")


class AIRateLimitError(AIAnalysisError):
    def __init__(self, message: str = "The AI service is experiencing high traffic. Please try again in a moment."):
        super().__init__(message, code="AI_RATE_LIMIT")


class AITimeoutError(AIAnalysisError):
    def __init__(self, message: str = "The AI analysis request timed out. Please try again."):
        super().__init__(message, code="AI_TIMEOUT")


class AIMalformedResponseError(AIAnalysisError):
    def __init__(self, message: str = "The AI response could not be validated against the clinical report schema."):
        super().__init__(message, code="AI_MALFORMED_RESPONSE")


def extract_json_from_text(raw: str) -> Dict[str, Any]:
    """Safely extracts JSON object from LLM response text, stripping markdown if present."""
    if not raw or not raw.strip():
        raise ValueError("Empty response received from AI model.")

    clean_text = raw.strip()
    
    # Strip markdown code blocks like ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", clean_text)
    if match:
        clean_text = match.group(1).strip()
    else:
        # If there are braces, locate outermost { ... }
        start = clean_text.find("{")
        end = clean_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            clean_text = clean_text[start : end + 1]

    return json.loads(clean_text)


class AIService:
    """Service to interact with configurable AI providers (Gemini, OpenAI, etc.)."""

    def __init__(self):
        self.client = httpx.Client(timeout=60.0)

    def _determine_provider(self) -> str:
        """Determines AI provider: 'gemini' or 'openai'."""
        provider = settings.AI_PROVIDER.lower()
        if provider in ["gemini", "openai"]:
            return provider

        # Auto-detect from key or model name
        key = settings.AI_API_KEY.strip()
        model = settings.AI_MODEL.lower()
        if key.startswith("AIza") or "gemini" in model:
            return "gemini"
        elif key.startswith("sk-") or "gpt" in model:
            return "openai"
        return "gemini"

    def _call_gemini_api(self, prompt: str, retry_instruction: Optional[str] = None) -> str:
        """Calls Google Gemini REST API."""
        if not settings.AI_API_KEY:
            raise AIServiceUnavailableError(
                "AI API key is not configured. Please set AI_API_KEY in the backend environment."
            )

        system_instruction = CLINICAL_REVIEW_SYSTEM_PROMPT
        full_prompt = prompt
        if retry_instruction:
            full_prompt = f"{prompt}\n\n[CORRECTION REQUIRED]: {retry_instruction}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [{"text": system_instruction}]
            },
            "generationConfig": {
                "temperature": 0.0,
                "responseMimeType": "application/json"
            }
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": settings.AI_API_KEY,
        }

        # Candidate models with primary model first
        models_to_try = [settings.AI_MODEL]
        for fallback in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error = None
        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.AI_API_KEY}"
            try:
                response = self.client.post(url, headers=headers, json=payload, timeout=45.0)
                if response.status_code == 429:
                    raise AIRateLimitError()
                if response.status_code in [500, 502, 503, 504]:
                    last_error = f"Model {model_name} service unavailable (HTTP {response.status_code})"
                    logger.warning(f"{last_error}. Attempting candidate model if available...")
                    continue
                if response.status_code == 404:
                    continue
                response.raise_for_status()

                data = response.json()
                candidates = data.get("candidates", [])
                if not candidates:
                    raise AIMalformedResponseError("AI returned no candidates.")
                
                parts = candidates[0].get("content", {}).get("parts", [])
                if not parts:
                    raise AIMalformedResponseError("AI returned no content parts.")
                
                return parts[0].get("text", "")
            except (AIRateLimitError, AIMalformedResponseError):
                raise
            except httpx.TimeoutException:
                last_error = "Timeout occurred"
                continue
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Error calling {model_name}: {str(e)}")
                continue

        raise AIServiceUnavailableError(f"Error communicating with AI service: {last_error}")

    def _call_openai_api(self, prompt: str, retry_instruction: Optional[str] = None) -> str:
        """Calls OpenAI or OpenAI-compatible REST API."""
        if not settings.AI_API_KEY:
            raise AIServiceUnavailableError(
                "AI API key is not configured. Please set AI_API_KEY in the backend environment."
            )

        base_url = settings.AI_BASE_URL.strip() or "https://api.openai.com/v1"
        url = f"{base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "Content-Type": "application/json"
        }

        messages = [
            {"role": "system", "content": CLINICAL_REVIEW_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        if retry_instruction:
            messages.append({"role": "user", "content": f"[CORRECTION]: {retry_instruction}"})

        payload = {
            "model": settings.AI_MODEL,
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
            "messages": messages
        }

        try:
            response = self.client.post(url, headers=headers, json=payload)
            if response.status_code == 429:
                raise AIRateLimitError()
            if response.status_code in [500, 502, 503, 504]:
                raise AIServiceUnavailableError()
            response.raise_for_status()

            data = response.json()
            choices = data.get("choices", [])
            if not choices:
                raise AIMalformedResponseError("AI returned no choices.")
            
            return choices[0].get("message", {}).get("content", "")
        except httpx.TimeoutException:
            raise AITimeoutError()
        except (AIRateLimitError, AIServiceUnavailableError, AIMalformedResponseError):
            raise
        except Exception as e:
            logger.error(f"OpenAI API request error: {str(e)}")
            raise AIServiceUnavailableError(f"Error communicating with AI service: {str(e)}")

    def _call_model(self, prompt: str, retry_instruction: Optional[str] = None) -> str:
        """Dispatches request to appropriate provider."""
        provider = self._determine_provider()
        logger.info(f"Dispatching AI analysis to provider: {provider}, model: {settings.AI_MODEL}")
        if provider == "openai":
            return self._call_openai_api(prompt, retry_instruction)
        return self._call_gemini_api(prompt, retry_instruction)

    def analyze_clinical_document(
        self,
        document_text: str,
        source_metadata: Optional[Dict[str, Any]] = None
    ) -> StructuredClinicalReport:
        """Main method to execute clinical document review with hallucination controls,
        safe parsing, retry on malformed JSON, and Pydantic validation.
        """
        logger.info("Starting AI clinical analysis on extracted text...")
        user_prompt = build_clinical_review_prompt(document_text, source_metadata)

        # First attempt
        raw_output = self._call_model(user_prompt)
        
        parsed_dict = None
        try:
            parsed_dict = extract_json_from_text(raw_output)
            validated_report = StructuredClinicalReport(**parsed_dict)
            logger.info("AI clinical analysis successfully validated on first attempt.")
            return validated_report
        except (json.JSONDecodeError, ValueError, ValidationError) as parse_err:
            logger.warning(f"Initial AI response parsing/validation failed: {str(parse_err)}. Retrying once...")

        # Single retry attempt with explicit error context
        retry_prompt = (
            "Your previous output was invalid or failed JSON schema validation. "
            "Return strictly raw, valid JSON adhering to the StructuredClinicalReport schema without markdown ticks."
        )
        retry_raw_output = self._call_model(user_prompt, retry_instruction=retry_prompt)

        try:
            parsed_dict = extract_json_from_text(retry_raw_output)
            validated_report = StructuredClinicalReport(**parsed_dict)
            logger.info("AI clinical analysis successfully validated on retry attempt.")
            return validated_report
        except Exception as retry_err:
            logger.error(f"AI response failed schema validation after retry: {str(retry_err)}")
            raise AIMalformedResponseError(
                f"The AI model produced an output that could not be validated against the clinical schema: {str(retry_err)}"
            )


ai_service = AIService()
