import chainlit as cl
import openai
import os
import base64
from prompts import SYSTEM_PROMPT, NUTRITION_SYSTEM_PROMPT
import json
from nutrition_helper import get_nutrition_info

from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.core.callbacks import CallbackManager
from langfuse.llama_index import LlamaIndexCallbackHandler

from langfuse.decorators import observe
from langfuse.openai import AsyncOpenAI

# Load environment variables
load_dotenv()

# Set up tracing
langfuse_callback_handler = LlamaIndexCallbackHandler()
Settings.callback_manager = CallbackManager([langfuse_callback_handler])

# OpenAI configuration
#api_key = os.getenv("OPENAI_API_KEY")
#endpoint_url = "https://api.openai.com/v1"

# https://platform.openai.com/docs/models/gpt-4o
"""model_kwargs = {
    "model": "chatgpt-4o-latest",
    "temperature": 0.3,
    "max_tokens": 500
}"""

gen_kwargs = {
    "model": "gpt-4o",
    "temperature": 0.2,
    "max_tokens": 500
}

# Mistral AI configuration
#api_key = os.getenv("RUNPOD_API_KEY")
#runpod_serverless_id = os.getenv("RUNPOD_SERVERLESS_ID")
#endpoint_url = f"https://api.runpod.ai/v2/{runpod_serverless_id}/openai/v1"

#model_kwargs = {
#    "model": "mistralai/Mistral-7B-Instruct-v0.3",
#    "temperature": 0.3,
#    "max_tokens": 500
#}

client = AsyncOpenAI()
#openai.AsyncClient(api_key=api_key, base_url=endpoint_url)

@observe
async def generate_response(client, message_history, gen_kwargs):
    response_message = cl.Message(content="")
    await response_message.send()

    stream = await client.chat.completions.create(messages=message_history, stream=True, **gen_kwargs)
    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await response_message.stream_token(token)

    await response_message.update()

    return response_message

async def fetch_nutrition_info(message_history):
    temp_message_history = message_history.copy()
    temp_message_history[0] = {"role": "system", "content": NUTRITION_SYSTEM_PROMPT}
    temp_message_history.append({"role": "system", "content": NUTRITION_SYSTEM_PROMPT})

    response_message = await client.chat.completions.create(messages=temp_message_history, **gen_kwargs)

    response_message = response_message.choices[0].message.content

    #response_message = await generate_response(client, message_history, gen_kwargs)
    print("Nutrition response is " + response_message)

    data = json.loads(response_message)
    if data:
        recipe_name = data['recipe_name']
        ingredients = data['ingredients']
        print(f"recipe name: {recipe_name} ingredients: {ingredients}")
        if recipe_name and ingredients:
            nutrition_info = get_nutrition_info(recipe_name, ingredients)
            print(nutrition_info)
            message_history.append({"role": "system", "content": rf"CONTEXT: {nutrition_info}"})
        else:
            print("Missing recipe name or ingredients for get_nutrition_info")

@cl.on_message
async def on_message(message: cl.Message):
      # Maintain an array of messages in the user session
    message_history = cl.user_session.get("message_history", [])
    if (not message_history or message_history[0].get("role") != "system"):
        message_history.insert(0, {"role": "system", "content": SYSTEM_PROMPT})

    message_history.append({"role": "user", "content": message.content})

    await fetch_nutrition_info(message_history)

    response_message = await generate_response(client, message_history, gen_kwargs)

    # Record the AI's response in the history
    message_history.append({"role": "assistant", "content": response_message.content})
    cl.user_session.set("message_history", message_history)

    # https://platform.openai.com/docs/guides/chat-completions/response-format


@cl.on_chat_start
async def main():
    #documents = SimpleDirectoryReader("data").load_data()
    #index = VectorStoreIndex.from_documents(documents)
    #langfuse_callback_handler.flush()

    message_history = [{"role": "system", "content": SYSTEM_PROMPT}]
    cl.user_session.set("message_history", message_history)
