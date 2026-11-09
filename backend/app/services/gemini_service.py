import json
import logging
from typing import Any, Optional
from google import genai
from google.genai import types

from app.core.config import settings
from app.schemas.milestone import GeminiProjectAnalysisSchema
from app.schemas.submission import GeminiDeliverableEvaluationSchema

logger = logging.getLogger(__name__)


class GeminiService:
    """Service wrapper for Google Gemini AI using the official google-genai SDK."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self._client: Optional[genai.Client] = None

    def _get_client(self) -> genai.Client:
        """Initialize and return the GenAI client, verifying API key availability."""
        if not self.api_key or not self.api_key.strip():
            logger.error("Attempted to call Gemini API without GEMINI_API_KEY configured.")
            raise ValueError(
                "Gemini API key is not configured. Please set GEMINI_API_KEY in the backend environment."
            )
        if self._client is None:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def _get_candidate_models(self) -> list[str]:
        """Return candidate models in order of priority, adapting for retired model names."""
        primary = self.model
        if primary in ("gemini-2.5-flash", "gemini-1.5-flash", "Gemini 2.5 Flash"):
            primary = "gemini-3.5-flash"
        candidates = [primary]
        for m in ("gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"):
            if m not in candidates:
                candidates.append(m)
        return candidates

    def generate_milestone_plan(
        self,
        prompt: str,
        system_instruction: str,
    ) -> GeminiProjectAnalysisSchema:
        """Call Gemini to generate a structured project analysis and milestone decomposition."""
        client = self._get_client()
        candidate_models = self._get_candidate_models()

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,  # Low temperature for deterministic, consistent structuring
            response_mime_type="application/json",
            response_schema=GeminiProjectAnalysisSchema,
        )

        last_error = None
        for model_name in candidate_models:
            logger.info("Calling Gemini model %s for milestone generation...", model_name)
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )

                if not response.text:
                    raise ValueError("Gemini returned an empty response.")

                # Parse and validate structured output
                raw_data = json.loads(response.text)
                validated_output = GeminiProjectAnalysisSchema.model_validate(raw_data)
                logger.info(
                    "Gemini (%s) successfully generated %d milestones (complexity: %s)",
                    model_name,
                    len(validated_output.milestones),
                    validated_output.project_complexity,
                )
                return validated_output

            except ValueError:
                raise
            except Exception as exc:
                last_error = exc
                logger.warning("Gemini model %s call failed (%s: %s). Trying next fallback...", model_name, type(exc).__name__, str(exc))

        logger.error("All Gemini candidate models failed: %s", last_error)
        raise RuntimeError(f"Gemini service failure: {type(last_error).__name__}") from None

    def evaluate_deliverable(
        self,
        contents: Any,
        system_instruction: str,
    ) -> GeminiDeliverableEvaluationSchema:
        """Call Gemini to evaluate deliverable submission evidence against agreed acceptance criteria."""
        client = self._get_client()
        candidate_models = self._get_candidate_models()

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.1,  # Strict, deterministic evaluation
            response_mime_type="application/json",
            response_schema=GeminiDeliverableEvaluationSchema,
        )

        last_error = None
        for model_name in candidate_models:
            logger.info("Calling Gemini model %s for deliverable evidence evaluation...", model_name)
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config=config,
                )

                if not response.text:
                    raise ValueError("Gemini returned an empty evaluation response.")

                raw_data = json.loads(response.text)
                validated_output = GeminiDeliverableEvaluationSchema.model_validate(raw_data)
                logger.info(
                    "Gemini (%s) successfully evaluated %d criteria",
                    model_name,
                    len(validated_output.criterion_evaluations),
                )
                return validated_output

            except ValueError:
                raise
            except Exception as exc:
                last_error = exc
                logger.warning("Gemini model %s evaluation failed (%s). Trying next fallback...", model_name, type(exc).__name__)

        logger.error("All Gemini evaluation candidate models failed: %s", last_error)
        raise RuntimeError(f"Gemini evaluation failure: {type(last_error).__name__}") from None


# Default shared service instance
gemini_service = GeminiService()

