import discord
from config import DISCORD_BOT_TOKEN
from gemini_api import generate_text
import asyncio
import os
from fastapi import FastAPI
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    logging.info(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    logging.info(f"Message from {message.author}: {message.content}")
    if message.author == client.user:
        logging.info("Message from myself, ignoring")
        return
    if "jimmy say" in message.content.lower():
        logging.info("Detected 'jimmy say' keyword")
        await message.channel.send("Jimmy is a genius!")
    else:
        logging.info("No keyword detected, invoking Gemini API")
        prompt = message.content
        response = generate_text(prompt)
        await message.channel.send(response)

async def start_discord_bot():
    await client.start(DISCORD_BOT_TOKEN)

app = FastAPI()

@app.get("/")
async def health_check():
    return {"status": "OK"}

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_discord_bot())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))