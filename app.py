import argparse

import dotenv

parser = argparse.ArgumentParser(description="Run a bot.")
parser.add_argument("-b", type=str, help="which bot to run", choices=["discord", "tg"], required=True)
parser.add_argument("-env-file", type=str, help="env file", default=".env")
args = parser.parse_args()

dotenv.load_dotenv(dotenv_path=args.env_file)

match args.b:
    case "discord":
        import discord_bot

        discord_bot.start()
    case "tg":
        import telegram_bot

        telegram_bot.start()
