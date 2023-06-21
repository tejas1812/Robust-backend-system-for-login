# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Install production dependencies.
COPY ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app
COPY . /app
ENV GOOGLE_APPLICATION_CREDENTIALS=
EXPOSE 80
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]

