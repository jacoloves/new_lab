FROM python:3.12-slim

RUN pip install flask
COPY --chmod=755 app.py /app.py
CMD [ "/app.py" ]
