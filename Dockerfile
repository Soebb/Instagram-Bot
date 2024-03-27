FROM python:3.10-slim-bookworm
ARG USER=root
USER $USER
RUN python3 -m venv venv
WORKDIR /app
COPY . ./
RUN apt-get update && apt-get -y install python3-pip ffmpeg
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["python3", "main.py"]
