import re
import traceback

import dotenv

dotenv.load_dotenv()

import discord
from discord import app_commands

from libs.config import Settings
from libs.llm import LLMAgentExecutor

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
config = Settings()  # type: ignore
llmAgent = LLMAgentExecutor(config=config)


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
        user_id = f"discord-{message.author.id}"
        async with message.channel.typing():
            try:
                if message.attachments:
                    for attachment in message.attachments:
                        if any(
                            attachment.filename.lower().endswith(ext)
                            for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]
                        ):
                            await message.add_reaction("🎨")
                            cont = []
                            if raw_content:
                                cont.append({"type": "text", "text": raw_content})
                            cont.append({"type": "image_url", "image_url": attachment.url})
                            response = llmAgent.query(user_id, cont)  # type: ignore
                            chunks = "".join([r async for r in response])
                            llmAgent.save_history(user_id, raw_content, chunks)
                            await message.channel.send(chunks, reference=message)
                else:
                    if "$clear" == raw_content:
                        llmAgent.clear_history(str(message.author.id))
                        await message.channel.send("🤖 Chat history has been reset.", reference=message)
                        return
                    await message.add_reaction("💬")

                    if (not raw_content) and message.reference and message.reference.message_id:
                        origin = await message.channel.fetch_message(message.reference.message_id)
                        if origin and origin.content:
                            raw_content = origin.content

                    response = llmAgent.query(user_id, raw_content)
                    chunks = "".join([r async for r in response])
                    llmAgent.save_history(user_id, raw_content, chunks)
                    await message.channel.send(chunks, reference=message)
            except Exception as e:
                traceback.print_exc()
                await message.channel.send(f"🤖 {e}", reference=message)


client.run(config.discord_bot_token)
