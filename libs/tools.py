from typing import Optional

from langchain.tools.openweathermap.tool import OpenWeatherMapQueryRun
from langchain_core.callbacks import CallbackManagerForToolRun
from langchain_core.language_models.llms import BaseLanguageModel
from langchain_core.tools import BaseTool


class AzureDallERun(BaseTool):
    """Tool that uses DALL-E to draw a picture."""

    client: BaseLanguageModel
    name: str = "Dall-E-Image-Generator"
    description: str = "A wrapper around Azure OpenAI DALL-E API. Useful for when you need to generate images from a text description. Input should be an image description."

    def _run(self, input: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the DALLEQueryRun tool."""
        return self.client.invoke(input=input)


class OpenWeatherMapQueryRunEnhanced(OpenWeatherMapQueryRun):
    description = (
        "A wrapper around OpenWeatherMap API. "
        "Useful for fetching current weather information for a specified location. "
        "Input should be a location string (e.g. London,GB). If it's a Chinese place name, it needs to be converted into the corresponding English place name."
        "**NOTE**: Make sure to confirm that the user is asking about the weather."
    )

    def _run(self, location: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the OpenWeatherMap tool."""
        return self.api_wrapper.run(location)
