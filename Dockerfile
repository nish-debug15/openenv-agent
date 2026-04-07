FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir fastapi uvicorn openai

RUN pip install --no-cache-dir -r server/requirements.txt || true

ENV PORT=7860

EXPOSE 7860

CMD ["python", "-m", "server.app"]