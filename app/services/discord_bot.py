import logging
import re

import nextcord
from nextcord.ext import commands

from app.ai_core.agents import LLMAgentExecutor
from app.config.settings import Settings
from app.services.http_api import PasteService

logger = logging.getLogger(__name__)
config = Settings()
llmAgent = LLMAgentExecutor(config=config)
paste_service = PasteService()


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


intents = nextcord.Intents.default()
intents.message_content = True
bot = Bot(intents=intents)


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")


@bot.event
async def on_message(message: nextcord.Message):
    if message.author == bot.user or message.mention_everyone:  # ignore this bot and disable @everyone
        return

    # @ or dm or role mentioned
    role_mentioned = message.guild and [role for role in message.role_mentions if role in message.guild.me.roles]
    if bot.user.mentioned_in(message) or isinstance(message.channel, nextcord.DMChannel) or role_mentioned:  # type: ignore[union-attr]
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
                            response = llmAgent.query(user_id, cont)  # type: ignore[arg-type]
                            chunks = "".join([r async for r in response])
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
                if len(chunks) > 2000:
                    d = await paste_service.create_paste(data=chunks)
                    suffix = f" [:link: click here to see more text ...]({d})"
                    await message.channel.send(chunks[: 2000 - len(suffix)] + suffix, reference=message)
                    return
                await message.channel.send(chunks, reference=message)
            except Exception as e:
                logger.error(f"Error: {e}")
                await message.channel.send(f"🤖 {e}", reference=message)


def start():
    bot.run(config.discord_bot_token)
