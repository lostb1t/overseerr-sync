FROM python:3.12-slim-bookworm
RUN pip install -r requirements.txt
CMD ["python", "scr/main.py"]