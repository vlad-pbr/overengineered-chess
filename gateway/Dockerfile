FROM docker.io/library/python:3.8.15-slim
WORKDIR /app
EXPOSE 8000
COPY requirements.txt requirements.txt
RUN python3.8 -m pip install -r ./requirements.txt
COPY . .
ENTRYPOINT [ "/usr/local/bin/gunicorn" ]
CMD [ "gateway:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--timeout", "0", "--bind", "0.0.0.0:8000" ]