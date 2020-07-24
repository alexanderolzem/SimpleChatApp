FROM python:3.8-slim
COPY server.py server.py
CMD python3 server.py
