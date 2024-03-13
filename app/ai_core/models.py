from typing import Any, Dict, List, Optional

from google.generativeai.types import safety_types  # type: ignore[import-untyped]
from langchain_google_genai import ChatGoogleGenerativeAI


class ChatGoogleGenerativeAIWithoutSafety(ChatGoogleGenerativeAI):
    safety_level: str | None = (
        "BLOCK_NONE"  # values: BLOCK_NONE, BLOCK_ONLY_HIGH, BLOCK_MEDIUM_AND_ABOVE, BLOCK_LOW_AND_ABOVE, HARM_BLOCK_THRESHOLD_UNSPECIFIED
    )
    safety_settings: safety_types.SafetySettingOptions | None

    def _prepare_params(self, stop: Optional[List[str]], **kwargs: Any) -> Dict[str, Any]:
        if self.safety_level and not self.safety_settings:
            self.safety_settings = [
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": self.safety_level,
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": self.safety_level,
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": self.safety_level,
                },
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": self.safety_level,
                },
            ]
        return super()._prepare_params(stop=stop, safety_settings=self.safety_settings, **kwargs)
