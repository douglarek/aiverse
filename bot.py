import os
import re

import discord
import dotenv
from discord import app_commands

from llm import DiscordChain

dotenv.load_dotenv()


intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
llmChain = DiscordChain()


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await tree.sync()


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:  # ignore this bot
        return

    # @ or dm
    if client.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):  # type: ignore
        raw_content = re.compile(r"<[^>]+>").sub("", message.content).lstrip()
        async with message.channel.typing():
            if "new chat" == raw_content:
                llmChain.reset_memory(str(message.author.id))
                await message.channel.send("🤖 Chat history has been reset.", reference=message)
                return
            await message.add_reaction("💬")
            response = await llmChain.query(str(message.author.id), raw_content)
            await message.channel.send(response, reference=message)


@tree.command(name="clear_history", description="Clear GPT4 chat history")  # type: ignore
async def clear_history(interaction: discord.Interaction):
    llmChain.reset_memory(str(interaction.user.id))
    await interaction.response.send_message("🤖 Chat history has been reset.")


client.run(os.getenv("DISCORD_BOT_TOKEN", ""))
