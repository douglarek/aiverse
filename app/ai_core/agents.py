import base64
from operator import itemgetter
from typing import Any, AsyncIterator, Dict, List, Union
from venv import logger

import boto3  # type: ignore[import]
import httpx
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.base import create_openai_functions_agent
from langchain.memory import ConversationTokenBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.google_search.tool import GoogleSearchRun
from langchain.tools.wikipedia.tool import WikipediaQueryRun
from langchain.utilities.google_search import GoogleSearchAPIWrapper
from langchain.utilities.wikipedia import WikipediaAPIWrapper
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models.bedrock import BedrockChat
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_community.chat_models.volcengine_maas import VolcEngineMaasChat
from langchain_core.language_models.llms import BaseLanguageModel
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
from langchain_groq.chat_models import ChatGroq
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_openai import ChatOpenAI, OpenAI

from app.ai_core.tools import (
    DallEAPIWrapperRun,
    OpenWeatherMapQueryRunEnhanced,
    TwitterTranslatorRun,
)
from app.config.settings import Settings


def text_model_from_config(config: Settings) -> BaseLanguageModel:
    if config.is_openai:
        return ChatOpenAI(
            model=config.openai_model_name,
            temperature=config.temperature,
            max_retries=config.max_retries,
        )

    if config.is_mistral:
        return ChatMistralAI(
            temperature=config.temperature, model=config.mistral_model, max_retries=config.max_retries
        )

    if config.is_google:
        return ChatGoogleGenerativeAI(  # type: ignore[arg-type,call-arg]
            model="gemini-pro",
            temperature=config.temperature,
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            },
            convert_system_message_to_human=True,
            max_retries=config.max_retries,
        )

    if config.is_groq:
        return ChatGroq(temperature=0, model=config.groq_model, max_retries=config.max_retries)

    if config.is_anthropic:
        return ChatAnthropic(temperature=config.temperature, model_name=config.claude_model)

    if config.is_dashscope:
        return ChatTongyi(model=config.dashscope_model, max_retries=config.max_retries)  # type: ignore[call-arg]

    if config.is_volcengine:
        return VolcEngineMaasChat(model=config.volcengine_model, temperature=config.temperature, max_retries=config.max_retries)  # type: ignore[call-arg]

    if config.is_aws_bedrock:
        c = boto3.client(
            service_name=config.aws_bedrock_service_name,
            region_name=config.aws_bedrock_region_name,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
        )
        return BedrockChat(
            client=c,
            model_id=config.aws_bedrock_model_id,
            model_kwargs={"temperature": config.temperature},
        )

    raise ValueError("Unknown model type.")


def vison_model_from_config(config: Settings) -> BaseLanguageModel | None:
    if config.is_openai:
        return ChatOpenAI(model="gpt-4-vision-preview")

    if config.is_google:
        return ChatGoogleGenerativeAI(  # type: ignore[arg-type,call-arg]
            model="gemini-pro-vision",
            temperature=config.temperature,
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            },
            convert_system_message_to_human=True,
            max_retries=config.max_retries,
        )

    if config.is_anthropic:
        return ChatAnthropic(temperature=config.temperature, model_name=config.claude_model)

    if config.is_aws_bedrock:
        c = boto3.client(
            service_name=config.aws_bedrock_service_name,
            region_name=config.aws_bedrock_region_name,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
        )
        return BedrockChat(
            client=c,
            model_id=config.aws_bedrock_model_id,
            model_kwargs={"temperature": config.temperature},
        )

    return None


def dalle_model_from_config(config: Settings) -> BaseLanguageModel | None:
    if config.is_openai:
        return OpenAI(temperature=config.temperature, max_retries=config.max_retries)

    return None


class LLMAgentExecutor:
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful AI assistant."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    history = dict[str, ConversationTokenBufferMemory]()

    def __init__(self, config: Settings):
        self.text_model = text_model_from_config(config=config)
        self.vision_model = vison_model_from_config(config=config)
        self.dalle_model = dalle_model_from_config(config=config)
        self.config = config
        self.history_max_size = config.history_max_size

    def get_history(self, user: str) -> ConversationTokenBufferMemory:
        m = self.history.get(
            user,
            ConversationTokenBufferMemory(
                llm=self.text_model,
                return_messages=True,
                max_token_limit=self.history_max_size,
                memory_key="history",
                output_key="output",  # for hacky reasons
            ),
        )
        self.history[user] = m
        return m

    def clear_history(self, user: str):
        if user in self.history:
            self.history[user].clear()

    def save_history(self, user: str, input: str, response: str):
        self.get_history(user).save_context({"input": input}, {"output": response})

    async def query(self, user: str, message: Union[str, List[Union[str, Dict]]]) -> AsyncIterator[str]:
        logger.info(f"Querying {user} with {message}")
        if isinstance(message, list):
            if self.vision_model:
                if isinstance(self.vision_model, ChatAnthropic) or isinstance(self.vision_model, BedrockChat):
                    async with httpx.AsyncClient() as client:
                        r = await client.get(message[1].get("image_url"))  # type: ignore[arg-type,union-attr]
                        img_base64 = base64.b64encode(r.content).decode("utf-8")
                        message[1]["image_url"] = {"url": f"data:image/png;base64,{img_base64}"}  # type: ignore[index]
                elif isinstance(self.vision_model, ChatOpenAI):
                    message[1]["image_url"] = {"url": message[1].get("image_url")}  # type: ignore[index,union-attr]
                msg = HumanMessage(content=message)
                async for s in self.vision_model.astream([msg]):
                    yield s.content  # type: ignore
                return
            raise ValueError("Vision model is not enabled")

        memory = self.get_history(user)

        tools: List[Any] = []
        if self.config.enable_google_search:
            tools.append(GoogleSearchRun(api_wrapper=GoogleSearchAPIWrapper()))  # type: ignore[call-arg]
        if self.config.enable_wikipedia:
            tools.append(WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper()))  # type: ignore[call-arg]
        if self.config.openweathermap_api_key:
            tools.append(OpenWeatherMapQueryRunEnhanced())
        if self.dalle_model and isinstance(self.dalle_model, OpenAI):
            tools.append(DallEAPIWrapperRun(client=self.dalle_model))  # type: ignore[call-arg]
        if self.config.enable_twitter_translator:
            tools.append(TwitterTranslatorRun())

        if self.config.is_openai and len(tools) > 0:
            self.prompt.append(MessagesPlaceholder(variable_name="agent_scratchpad"))
            # self.prompt.append can't update input_variables, so need this
            self.prompt.input_variables.append("agent_scratchpad")
            agent = create_openai_functions_agent(self.text_model, tools, self.prompt)
            agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)  # type: ignore[arg-type]
            async for v in agent_executor.astream(
                {"input": message, "history": memory.load_memory_variables({})[memory.memory_key]}
            ):
                if isinstance(v, dict) and "output" in v:
                    yield v["output"]
            return

        chain = (
            RunnablePassthrough.assign(history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))
            | self.prompt
            | self.text_model
        )

        async for c in chain.astream({"input": message}):
            try:
                yield c.content
            except StopIteration:
                pass
