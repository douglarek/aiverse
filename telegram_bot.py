import logging
import re
from typing import Tuple, no_type_check

import dotenv

dotenv.load_dotenv()


from telegram import BotCommand, PhotoSize, Update
from telegram.constants import ParseMode
from telegram.error import BadRequest
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from libs.config import Settings
from libs.llm import LLMAgentExecutor

config = Settings()  # type: ignore

llmAgent = LLMAgentExecutor(config=config)

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Telegram always provides various sizes of single photos.
@no_type_check
def get_largest_photo_size(photos: Tuple[PhotoSize]) -> PhotoSize:
    largest_photo = photos[0]
    for photo_data in photos:
        if largest_photo.file_size < photo_data.file_size:
            largest_photo = photo_data
    return largest_photo


################################

# A piece of magical code designed to handle the display of Markdown in Telegram. From H-T-H/Gemini-Telegram-Bot.


def find_all_index(str, pattern):
    index_list = [0]
    for match in re.finditer(pattern, str, re.MULTILINE):
        if match.group(1) != None:
            start = match.start(1)
            end = match.end(1)
            index_list += [start, end]
    index_list.append(len(str))
    return index_list


def replace_all(text, pattern, function):
    poslist = [0]
    strlist = []
    originstr = []
    poslist = find_all_index(text, pattern)
    for i in range(1, len(poslist[:-1]), 2):
        start, end = poslist[i : i + 2]
        strlist.append(function(text[start:end]))
    for i in range(0, len(poslist), 2):
        j, k = poslist[i : i + 2]
        originstr.append(text[j:k])
    if len(strlist) < len(originstr):
        strlist.append("")
    else:
        originstr.append("")
    new_list = [item for pair in zip(originstr, strlist) for item in pair]
    return "".join(new_list)


def escapeshape(text):
    return "▎*" + text.split()[1] + "*"


def escapeminus(text):
    return "\\" + text


def escapebackquote(text):
    return r"\`\`"


def escapeplus(text):
    return "\\" + text


def escape(text, flag=0):
    # In all other places characters
    # _ * [ ] ( ) ~ ` > # + - = | { } . !
    # must be escaped with the preceding character '\'.
    text = re.sub(r"\\\[", "@->@", text)
    text = re.sub(r"\\\]", "@<-@", text)
    text = re.sub(r"\\\(", "@-->@", text)
    text = re.sub(r"\\\)", "@<--@", text)
    if flag:
        text = re.sub(r"\\\\", "@@@", text)
    text = re.sub(r"\\", r"\\\\", text)
    if flag:
        text = re.sub(r"\@{3}", r"\\\\", text)
    text = re.sub(r"_", "\_", text)
    text = re.sub(r"\*{2}(.*?)\*{2}", "@@@\\1@@@", text)
    text = re.sub(r"\n{1,2}\*\s", "\n\n• ", text)
    text = re.sub(r"\*", "\*", text)
    text = re.sub(r"\@{3}(.*?)\@{3}", "*\\1*", text)
    text = re.sub(r"\!?\[(.*?)\]\((.*?)\)", "@@@\\1@@@^^^\\2^^^", text)
    text = re.sub(r"\[", "\[", text)
    text = re.sub(r"\]", "\]", text)
    text = re.sub(r"\(", "\(", text)
    text = re.sub(r"\)", "\)", text)
    text = re.sub(r"\@\-\>\@", "\[", text)
    text = re.sub(r"\@\<\-\@", "\]", text)
    text = re.sub(r"\@\-\-\>\@", "\(", text)
    text = re.sub(r"\@\<\-\-\@", "\)", text)
    text = re.sub(r"\@{3}(.*?)\@{3}\^{3}(.*?)\^{3}", "[\\1](\\2)", text)
    text = re.sub(r"~", "\~", text)
    text = re.sub(r">", "\>", text)
    text = replace_all(text, r"(^#+\s.+?$)|```[\D\d\s]+?```", escapeshape)
    text = re.sub(r"#", "\#", text)
    text = replace_all(text, r"(\+)|\n[\s]*-\s|```[\D\d\s]+?```|`[\D\d\s]*?`", escapeplus)
    text = re.sub(r"\n{1,2}(\s*)-\s", "\n\n\\1• ", text)
    text = re.sub(r"\n{1,2}(\s*\d{1,2}\.\s)", "\n\n\\1", text)
    text = replace_all(text, r"(-)|\n[\s]*-\s|```[\D\d\s]+?```|`[\D\d\s]*?`", escapeminus)
    text = re.sub(r"```([\D\d\s]+?)```", "@@@\\1@@@", text)
    text = replace_all(text, r"(``)", escapebackquote)
    text = re.sub(r"\@{3}([\D\d\s]+?)\@{3}", "```\\1```", text)
    text = re.sub(r"=", "\=", text)
    text = re.sub(r"\|", "\|", text)
    text = re.sub(r"{", "\{", text)
    text = re.sub(r"}", "\}", text)
    text = re.sub(r"\.", "\.", text)
    text = re.sub(r"!", "\!", text)
    return text


################################


@no_type_check
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    raw_message = update.message.text.removeprefix(context.bot.name).lstrip()
    user_id = f"telegram-{update.message.from_user.id}"
    await update.effective_chat.send_action(action="typing")

    chunks = ""
    placeholder = await update.message.reply_text("...")

    try:
        if update.effective_message.reply_to_message and update.effective_message.reply_to_message.photo:
            photo_size = get_largest_photo_size(update.effective_message.reply_to_message.photo)
            photo_file = await context.bot.get_file(photo_size.file_id)
            photo_file._get_encoded_url()
            cont = []
            if raw_message:
                cont.append({"type": "text", "text": raw_message})
            cont.append({"type": "image_url", "image_url": photo_file._get_encoded_url()})
            raw_message = cont

        response = llmAgent.query(user_id, raw_message)
        async for chunk in response:
            curr = chunks + chunk
            if curr != chunks:
                chunks = curr
                await placeholder.edit_text(curr)
        if isinstance(raw_message, str):
            llmAgent.save_history(user_id, raw_message, chunks)
        await placeholder.edit_text(" * *\n\n" + escape(chunks), parse_mode=ParseMode.MARKDOWN_V2)
    except Exception as e:
        if isinstance(e, BadRequest) and e.message.find("Message is not modified") != -1:
            return
        logger.exception(e)
        await placeholder.edit_text(f"🤖 An error has occurred: {e}")


@no_type_check
async def reset_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    llmAgent.clear_history(f"telegram-{update.message.from_user.id}")
    await update.message.reply_text("🤖 Chat history has been reset.")


async def app_post_init(application: Application) -> None:
    # setup bot commands
    await application.bot.set_my_commands(
        [
            BotCommand("reset", "clear the chat history"),
        ]
    )


user_filter = filters.User(username=config.telegram_allowed_users) if config.telegram_allowed_users else filters.ALL

"""Start the bot."""
# Create the Application and pass it your bot's token.
application = Application.builder().token(config.telegram_bot_token).post_init(app_post_init).build()

# on non command i.e message - echo the message on Telegram
application.add_handler(CommandHandler("reset", reset_command_handler, filters=user_filter))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & user_filter, callback=message_handler))

# Run the bot until the user presses Ctrl-C
application.run_polling(allowed_updates=Update.ALL_TYPES)
