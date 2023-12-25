import os
import re

import discord
import dotenv
from discord import app_commands

from llm import DiscordChain

dotenv.load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
HISTORY_MAX_SIZE = os.getenv("HISTORY_MAX_SIZE", "2048")


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
llmChain = DiscordChain(history_max_size=int(HISTORY_MAX_SIZE))


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}, {client.user.display_name}")
    await tree.sync()


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:  # ignore this bot
        return

    # @ or dm
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):  # type: ignore
        raw_content = re.compile(r"<[^>]+>").sub("", message.content).lstrip()
        async with message.channel.typing():
            if "$clear" == raw_content:
                llmChain.clear_history(str(message.author.id))
                await message.channel.send("🤖 Chat history has been reset.", reference=message)
                return
            await message.add_reaction("💬")
            response = await llmChain.query(str(message.author.id), raw_content)
            await message.channel.send(response, reference=message)


client.run(DISCORD_BOT_TOKEN)
