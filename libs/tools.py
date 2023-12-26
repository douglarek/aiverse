from typing import Optional

from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.language_models.llms import BaseLanguageModel
from langchain_core.tools import BaseTool


class DALLEQueryRun(BaseTool):
    """Tool that uses DALL-E to draw a picture."""

    client: BaseLanguageModel
    name: str = "Dall-E-Image-Generator"
    description: str = "A wrapper around Azure OpenAI DALL-E API. Useful for when you need to generate images from a text description. Input should be an image description."

    def _run(self, input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the DALLEQueryRun tool."""
        return self.client.invoke(input=input)
