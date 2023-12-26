from operator import itemgetter
from typing import Dict, List, Union

from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.ddg_search.tool import DuckDuckGoSearchResults
from langchain.tools.openweathermap.tool import OpenWeatherMapQueryRun
from langchain.tools.wikipedia.tool import WikipediaQueryRun
from langchain.utilities.duckduckgo_search import DuckDuckGoSearchAPIWrapper
from langchain.utilities.wikipedia import WikipediaAPIWrapper
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

from libs.config import Settings


def text_model_from_config(config: Settings) -> BaseChatModel:
    if config.is_azure:
        return AzureChatOpenAI(
            azure_deployment=config.azure_openai_deployment,
            api_version=config.azure_openai_api_version,
            temperature=config.temperature,
        )

    if config.is_google:
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=config.temperature)  # type: ignore

    raise ValueError("Only Azure and Google models are supported at this time")


def vison_model_from_config(config: Settings) -> BaseChatModel | None:
    if config.has_vision:
        return ChatGoogleGenerativeAI(model="gemini-pro-vision", temperature=config.temperature)  # type: ignore

    return None


class DiscordChain:
    prompt = ChatPromptTemplate.from_messages(
        [
            # ("system", "You are a helpful chatbot"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    history = dict[str, ConversationSummaryBufferMemory]()

    def __init__(self, config: Settings):
        self.text_model = text_model_from_config(config=config)
        self.vision_model = vison_model_from_config(config=config)
        self.history_max_size = config.history_max_size

    def get_history(self, user: str) -> ConversationSummaryBufferMemory:
        m = self.history.get(
            user,
            ConversationSummaryBufferMemory(
                llm=self.text_model,
                return_messages=True,
                max_token_limit=self.history_max_size,
                memory_key="chat_history",
            ),
        )
        self.history[user] = m
        return m

    def clear_history(self, user: str):
        if user in self.history:
            self.history[user].clear()

    async def query(self, user: str, message: Union[str, List[Union[str, Dict]]]) -> str:
        if isinstance(message, list):
            if self.vision_model:
                msg = HumanMessage(content=message)
                response = await self.vision_model.ainvoke([msg])
                return response.content  # type: ignore
            return "❌ Vision model is not available."

        memory = self.get_history(user)

        if isinstance(self.text_model, ChatGoogleGenerativeAI):
            chain = (
                RunnablePassthrough.assign(
                    history=RunnableLambda(memory.load_memory_variables) | itemgetter("chat_history")
                )
                | self.prompt
                | self.text_model
            )
            response = await chain.ainvoke({"input": message})
            memory.save_context({"input": message}, {"output": response.content})  # type: ignore
            return response.content  # type: ignore

        tools = [
            DuckDuckGoSearchResults(
                name="duckduckgo_search_results",
                api_wrapper=DuckDuckGoSearchAPIWrapper(max_results=7, safesearch="off"),
            ),
            WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()),  # type: ignore
            OpenWeatherMapQueryRun(),
        ]
        chain_agent = initialize_agent(
            tools,
            self.text_model,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=memory,
            verbose=True,
            handle_parsing_errors=True,
        )

        response = await chain_agent.ainvoke({"input": message})  # type: ignore
        memory.save_context({"input": message}, {"output": response["output"]})  # type: ignore
        return response["output"]  # type: ignore
