FROM python:3.11-slim

COPY . /src
WORKDIR /src

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]