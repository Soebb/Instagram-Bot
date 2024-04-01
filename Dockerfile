FROM python:3.10-slim-bookworm
#ARG USER=root
#USER $USER
#RUN python3 -m venv venv

RUN apt-get update && apt-get -y install python3-pip ffmpeg wget sudo libgtkmm-3.0-1v5 libnotify4 sqlite3
RUN wget https://ftp.mozilla.org/pub/firefox/releases/120.0/linux-x86_64/en-US/firefox-120.0.tar.bz2
RUN tar xjf firefox-120.0.tar.bz2 && mv firefox /opt && ln -s /opt/firefox/firefox /usr/local/bin/firefox
#RUN wget https://downloads.sourceforge.net/project/ubuntuzilla/mozilla/apt/pool/main/f/firefox-mozilla-build/firefox-mozilla-build_124.0.1-0ubuntu1_i386.deb
#RUN dpkg -i firefox-mozilla-build_124.0.1-0ubuntu1_i386.deb; apt-get -fy install
WORKDIR /app
COPY . ./
RUN pip3 install -r requirements.txt
EXPOSE 5000
RUN cd /home && ls -a -R
CMD ["python3", "main.py"]
