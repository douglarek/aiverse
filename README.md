# GPT-discord

## Introduction

This project is a Discord bot that uses the Discord API and various language models to interact with users. The bot can respond to messages, clear chat history, and more.

## Prerequisites

- Python 3.11 or higher
- Docker
- Docker Compose

## Setup

1. Clone the repository:

    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2. Create a [`.env`](.env) file in the root directory of the project and add your Discord bot token and other necessary environment variables. You can refer to [`env.example`](command:_github.copilot.openSymbolInFile?%5B%22env.example%22%2C%22env.example%22%5D "env.example") for the required environment variables.

    ```bash
    cp env.example .env
    # Edit .env with your own values
    ```

3. Build and run the Docker image:

    ```bash
    docker-compose up --build -d
    ```

## Usage

Once the bot is running, you can interact with it on Discord. Mention the bot in a message or send a direct message to the bot to get a response.

## Commands

- `$clear`: Clears the chat history.

## Contributing

Contributions are welcome! Please read the contributing guidelines before making any changes.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

## License

This project is licensed under the terms of the Apache-2.0 license.