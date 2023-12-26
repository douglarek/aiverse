import re

import dotenv

dotenv.load_dotenv()

import discord
from discord import app_commands

from libs.config import Settings
from libs.llm import DiscordAgentExecutor

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
config = Settings()  # type: ignore
llmAgent = DiscordAgentExecutor(config=config)


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
            if message.attachments:
                for attachment in message.attachments:
                    if any(
                        attachment.filename.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]
                    ):
                        await message.add_reaction("🎨")
                        cont = []
                        if raw_content:
                            cont.append({"type": "text", "text": raw_content})
                        cont.append({"type": "image_url", "image_url": attachment.url})
                        response = await llmAgent.query(str(message.author.id), cont)  # type: ignore
                        await message.channel.send(response, reference=message)
            else:
                if "$clear" == raw_content:
                    llmAgent.clear_history(str(message.author.id))
                    await message.channel.send("🤖 Chat history has been reset.", reference=message)
                    return
                await message.add_reaction("💬")
                response = await llmAgent.query(str(message.author.id), raw_content)
                await message.channel.send(response, reference=message)


client.run(config.discord_bot_token)
