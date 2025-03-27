import discord
from config import DISCORD_BOT_TOKEN
from gemini_api import process_prompt  # Import process_prompt instead of generate_text
import asyncio
import os
from fastapi import FastAPI
import logging
from io import BytesIO  # Import BytesIO
import aiohttp
import tempfile # Import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

async def download_image(url):
    """Downloads an image from a URL and returns it as bytes."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.read()
            else:
                return None

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
        user_id = str(message.author.id) # Get user id
        response = process_prompt(prompt, user_id)  # Use process_prompt and pass user_id
        if isinstance(response, str):
            await message.channel.send(response)
        elif isinstance(response, list):
            # Handle image responses
            for image in response:
                try:
                    # Save the image to a temporary file
                    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                        image.save(temp_file.name)
                        temp_file_name = temp_file.name

                    # Read the image from the temporary file into a BytesIO buffer
                    with open(temp_file_name, "rb") as f:
                        image_buffer = BytesIO(f.read())

                    # Send the image as a file
                    file = discord.File(fp=image_buffer, filename="generated_image.png")
                    await message.channel.send(file=file)

                    # Clean up the temporary file
                    os.remove(temp_file_name)
                except Exception as e:
                    logging.error(f"Error sending image: {e}")
                    await message.channel.send("Error generating or sending image.")
        else:
            logging.error("Unexpected response type from process_prompt")
            await message.channel.send("An unexpected error occurred.")

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
