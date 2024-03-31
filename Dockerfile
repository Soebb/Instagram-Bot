FROM python:3.10-slim-bookworm
ARG USER=root
USER $USER
#RUN python3 -m venv venv
WORKDIR /app
COPY . ./

RUN apt-get update && apt-get -y install python3-pip ffmpeg flatpak
RUN flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
RUN flatpak install flathub org.freedesktop.Platform//23.08
RUN flatpak install flathub org.mozilla.firefox
#RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#RUN dpkg -i google-chrome-stable_current_amd64.deb; apt-get -fy install
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD ["python3", "main.py"]
