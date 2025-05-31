# Part of Bob: an AI-driven learning and productivity portal for individuals and organizations | Copyright (c) 2025 | License: MIT
import openai
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


async def chat(messages):
    response = await openai.ChatCompletion.acreate(
        model="gpt-4", messages=messages
    )
    return response.choices[0].message["content"]
