import json
from typing import Any, List, Optional

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from openai import AzureOpenAI


class AzureDALLELLM(LLM):
    client: AzureOpenAI | None = None

    def __init__(
        self,
        *,
        api_version: str | None = None,
        azure_endpoint: str,
        azure_deployment: str | None = None,
        api_key: str | None = None,
    ) -> None:
        super().__init__()
        self.client = AzureOpenAI(
            api_version=api_version,
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            azure_deployment=azure_deployment,
        )

    @property
    def _llm_type(self) -> str:
        return "azure-custom-dalle"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        if stop is not None:
            raise ValueError("stop kwargs are not permitted.")
        assert self.client is not None
        result = self.client.images.generate(prompt=prompt, quality="standard", size="1024x1024", n=1)
        json_response = json.loads(result.model_dump_json())
        return json_response["data"][0]["url"]
