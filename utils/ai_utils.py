from ollama import Client

from resources.constants import OLLAMA_ENDPOINT

client = Client(
    host=OLLAMA_ENDPOINT,
)


def stream_llm_output(
    model: str, prompt: str, options={"temperature": 0.4, "top_p": 0.95}
):
    """
    Stream the output of a LLM deployed from Ollama.
    """

    stream = client.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
        options=options,
    )

    for chunk in stream:
        yield chunk["message"]["content"]
