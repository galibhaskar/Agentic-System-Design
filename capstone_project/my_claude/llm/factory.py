from enum import Enum

from my_claude.config import config
from my_claude.observability import get_logger

logger = get_logger(__name__)

class Provider(str, Enum):
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    HUGGINGFACE = "HUGGINGFACE"


def get_llm():
    """
    Factory function to create and return an LLM instance based on the configuration.
    """
    llm_model = config["llm"]["model"]
    llm_provider = config["llm"]["provider"]
    llm_temperature = config["llm"]["temperature"]

    if llm_provider == Provider.OPENAI:
        from langchain_openai import ChatOpenAI
        logger.info(f"Creating ChatOpenAI instance with model: {llm_model}, temperature: {llm_temperature}")
        return ChatOpenAI(model_name=llm_model, temperature=llm_temperature)
    elif llm_provider == Provider.ANTHROPIC:
        from langchain_anthropic import ChatAnthropic
        logger.info(f"Creating Anthropic instance with model: {llm_model}, temperature: {llm_temperature}")
        return ChatAnthropic(model_name=llm_model, temperature=llm_temperature)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")

def get_embedder():
    """
    Factory function to create and return an Embedder instance based on the configuration.
    """
    embedder_model = config["embedder"]["model"]
    embedder_provider = config["embedder"]["provider"]

    if embedder_provider == Provider.OPENAI:
        from langchain_openai import OpenAIEmbeddings
        logger.info(f"Creating OpenAIEmbeddings instance with model: {embedder_model}")
        return OpenAIEmbeddings(model=embedder_model)
    elif embedder_provider == Provider.HUGGINGFACE:
        from langchain_huggingface import HuggingFaceEmbeddings
        logger.info(f"Creating HuggingFaceEmbeddings instance with model: {embedder_model}")
        return HuggingFaceEmbeddings(model_name=embedder_model)
    else:
        raise ValueError(f"Unsupported Embedder provider: {embedder_provider}")