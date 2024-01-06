from typing import Optional

import httpx
from bs4 import BeautifulSoup
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


class TwitterTranslatorRun(BaseTool):
    """Tool that translate a tweet url to Simplified Chinese text."""

    name: str = "Twitter-Translator"
    description: str = "Useful for when you need to get a tweet content with a url and translate it to authentic Simplified Chinese. Input must be a tweet url like this: `https://fxtwitter.com/sama/status/1743385732147032262`."

    def _run(self, url: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Use the TwitterTranslatorRun tool."""
        if not url.startswith("https://fxtwitter.com/"):
            return "Invalid url. Please make sure the url starts with `https://fxtwitter.com/`."

        r = httpx.get(url=url)
        if r.status_code != 200:
            return f"Error: {r.status_code}, {r.text}"

        soup = BeautifulSoup(r.text, features="html.parser")
        title = soup.find("meta", property="og:title")
        desc = soup.find("meta", property="og:description")
        text = ""
        if title:
            text += title.get("content", "") + "\n"  # type: ignore
        if desc:
            text += desc.get("content", "") + "\n"  # type: ignore

        return text
