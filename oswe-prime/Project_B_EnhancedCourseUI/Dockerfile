FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
CMD ["bash","-lc","./run_tests.sh"]
