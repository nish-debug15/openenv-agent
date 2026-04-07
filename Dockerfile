FROM public.ecr.aws/huggingface/transformers-pytorch-cpu:latest

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install fastapi uvicorn openai

# optional deps
RUN pip install -r server/requirements.txt || true

ENV PORT=7860

EXPOSE 7860

CMD ["python", "-m", "server.app"]