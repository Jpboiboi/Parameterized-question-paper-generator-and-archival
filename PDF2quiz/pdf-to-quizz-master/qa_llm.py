from langchain.chat_models import ChatOpenAI  # Correct import for chat models
from callback import MyCallbackHandler
from langchain.callbacks.base import BaseCallbackManager

class QaLlm():

    def __init__(self) -> None:
        manager = BaseCallbackManager([MyCallbackHandler()])
        # Use ChatOpenAI instead of OpenAI
        self.llm = ChatOpenAI(temperature=0, model="gpt-3.5-turbo", callback_manager=manager)

    def get_llm(self):
        return self.llm
