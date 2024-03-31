FROM python:3.10-slim-bookworm
ARG USER=root
USER $USER
#RUN python3 -m venv venv
WORKDIR /app
COPY . ./

RUN apt-get update && apt-get -y install python3-pip ffmpeg wget sudo libgtkmm-3.0-1v5 libnotify4 sqlite3
RUN wget https://ftp.mozilla.org/pub/firefox/releases/125.0b6/linux-x86_64/en-US/firefox-125.0b6.tar.bz2
RUN tar xjf firefox-125.0b6.tar.bz2 && sudo mv firefox /opt && sudo ln -s /opt/firefox/firefox /usr/local/bin/firefox
#RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#RUN dpkg -i firefox-125.0b6.deb; apt-get -fy install

RUN pip3 install -r requirements.txt
EXPOSE 5000
RUN whereis firefox
CMD ["python3", "main.py"]
