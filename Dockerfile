FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r server/requirements.txt

RUN pip install --no-cache-dir openai

ENV PORT=7860

EXPOSE 7860

CMD ["python", "-m", "server.app"]