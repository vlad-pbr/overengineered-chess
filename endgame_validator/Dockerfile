FROM docker.io/library/python:3.8.15-slim
WORKDIR /app
COPY . .
RUN python3.8 -m pip install -r ./requirements.txt
ENTRYPOINT [ "/usr/bin/env", "python3.8" ]
CMD [ "./endgame_validator.py" ]