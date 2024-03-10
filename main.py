import argparse
import logging

import dotenv

parser = argparse.ArgumentParser(description="Run a bot.")
parser.add_argument("-env-file", type=str, help="env file", default=".env")
args = parser.parse_args()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    dotenv.load_dotenv(dotenv_path=args.env_file)
    import app.services.discord_bot as discord_bot

    discord_bot.start()
