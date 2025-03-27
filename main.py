import discord
from config import DISCORD_BOT_TOKEN
from gemini_api import generate_text

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    print(f"Message from {message.author}: {message.content}")
    if message.author == client.user:
        print("Message from myself, ignoring")
        return
    if "jimmy say" in message.content.lower():
        print("Detected 'jimmy say' keyword")
        await message.channel.send("Jimmy is a genius!")
    else:
        print("No keyword detected, invoking Gemini API")
        prompt = message.content
        response = generate_text(prompt)
        await message.channel.send(response)

client.run(DISCORD_BOT_TOKEN)