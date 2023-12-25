from operator import itemgetter

from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationTokenBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

from libs.config import Settings


def model_from_config(config: Settings) -> BaseChatModel:
    if config.azure_openai_endpoint and config.azure_openai_deployment and config.azure_openai_api_key:
        return AzureChatOpenAI(
            azure_deployment=config.azure_openai_deployment,
            api_version=config.azure_openai_api_version,
            temperature=config.temperature,
        )

    if config.google_api_key:
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=config.temperature)  # type: ignore

    raise ValueError("Only Azure and Google models are supported at this time")


class DiscordChain:
    prompt = ChatPromptTemplate.from_messages(
        [
            # ("system", "You are a helpful chatbot"),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    history = dict[str, ConversationTokenBufferMemory]()

    def __init__(self, config: Settings):
        self.model = model_from_config(config=config)
        self.history_max_size = config.history_max_size

    def get_history(self, user: str) -> ConversationTokenBufferMemory:
        m = self.history.get(
            user,
            ConversationTokenBufferMemory(llm=self.model, return_messages=True, max_token_limit=self.history_max_size),
        )
        self.history[user] = m
        return m

    def clear_history(self, user: str):
        if user in self.history:
            self.history[user].clear()

    async def query(self, user: str, message: str) -> str:
        memory = self.get_history(user)
        chain = (
            RunnablePassthrough.assign(history=RunnableLambda(memory.load_memory_variables) | itemgetter("history"))
            | self.prompt
            | self.model
        )

        response = await chain.ainvoke({"input": message})
        memory.save_context({"input": message}, {"output": response.content})  # type: ignore
        return response.content  # type: ignore
