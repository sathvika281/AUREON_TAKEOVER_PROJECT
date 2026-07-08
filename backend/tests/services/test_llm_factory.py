from aureon.services.llm.factory import get_llm_client
from aureon.services.llm.providers.groq_client import GroqClient


def test_factory_returns_groq_client_for_groq_provider(settings):
    client = get_llm_client(settings)
    assert isinstance(client, GroqClient)
