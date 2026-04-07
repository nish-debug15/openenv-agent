FROM python:3.9-buster

WORKDIR /app

COPY . .

RUN pip install --upgrade pip

RUN pip install fastapi uvicorn openai

RUN pip install -r server/requirements.txt || true

ENV PORT=7860

EXPOSE 7860

CMD ["python", "-m", "server.app"]