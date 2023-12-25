import os
from operator import itemgetter

from langchain.chat_models import AzureChatOpenAI
from langchain.memory import ConversationTokenBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI


def model_from_env() -> BaseChatModel:
    azure_key = os.getenv("AZURE_OPENAI_API_KEY")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-09-01-preview")
    google_api_key = os.getenv("GOOGLE_API_KEY")

    if azure_key and azure_endpoint and azure_deployment:
        return AzureChatOpenAI(azure_deployment=azure_deployment, api_version=azure_api_version, temperature=0.7)

    if google_api_key:
        return ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7)  # type: ignore

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

    def __init__(self, history_max_size: int):
        self.model = model_from_env()
        self.history_max_size = history_max_size

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
