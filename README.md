# LLMBot

This project includes a Discord bot and a Telegram bot that interact with users and process their messages.

## Supported Models

This project supports several models for processing user messages:

1. OpenAI's model, implemented in the `ChatOpenAI` class.
2. Azure's model, implemented in the `AzureChatOpenAI` class.
3. Mistral's model, implemented in the `ChatMistralAI` class.
4. Google's model, implemented in the `ChatGoogleGenerativeAI` class.
5. Google's vision model, also implemented in the `ChatGoogleGenerativeAI` class, with the model name "gemini-pro-vision".
6. Azure's DALL-E model, implemented in the `AzureDALLELLM` class.

The choice and initialization of these models are done in the `text_model_from_config`, `vison_model_from_config`, and `dalle_model_from_config` functions in the `libs/llm.py` file. The specific model used depends on the settings in the `Settings` configuration object.


## Discord Bot

The Discord bot is implemented in the `discord_bot.py` file. It uses the discord.py library to interact with the Discord API. The bot listens for messages and reacts to them based on certain conditions.

### Setup

0. Set up a virtual environment (optional, but recommended):
    ```sh
    python3 -m venv .venv
    source .venv/bin/activate
    ```
1. Create a `.env` file based on the provided `env.example` file.
2. Fill in the `DISCORD_BOT_TOKEN` with your bot's token.

### Running the Bot

Run the bot using the following command:

```sh
python discord_bot.py
```

The bot will log in and start listening for messages. It will respond to messages that mention it or are sent in a direct message (DM) channel. The bot also provides a `$clear` command to clear the chat history.

## Telegram Bot

The Telegram bot is implemented in the `telegram_bot.py` file. It uses the python-telegram-bot library to interact with the Telegram Bot API. The bot listens for messages and reacts to them based on certain conditions.

### Setup

1. Create a `.env` file based on the provided `env.example` file.
2. Fill in the `TELEGRAM_BOT_TOKEN` with your bot's token.
3. Optionally, fill in the `TELEGRAM_ALLOWED_USERS` with the usernames of users who are allowed to interact with the bot.

### Running the Bot

Run the bot using the following command:

```sh
python telegram_bot.py
```

The bot will start listening for messages. It will respond to messages from allowed users and ignore messages from other users. The bot also provides a `/clear` command to clear the chat history.

## Common Features

Both bots use the `LLMAgentExecutor` class from `libs/llm.py` to process user messages and generate responses. They also use the `Settings` class from `libs/config.py` to load configuration settings from the `.env` file.

## Contributing

Contributions are welcome! Please read the contributing guidelines before making any changes.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## License

This project is licensed under the Apache-2.0 License - see the LICENSE file for details.
