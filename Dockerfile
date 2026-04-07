FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r server/requirements.txt
RUN pip install --no-cache-dir openai uvicorn fastapi

ENV PORT=7860

EXPOSE 7860

CMD ["python", "-m", "server.app"]