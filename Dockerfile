FROM adoptopenjdk:latest
LABEL MAINTAINER ksg97031 (ksg97031@gmail.com)

# Install dependencies
RUN apt update && apt upgrade -y && apt install curl python3 python3-pip -y
RUN alias python=python3
RUN alias pip=pip3
# Install Frida
RUN pip3 install --upgrade pip && pip3 install frida

# Install apktool
ENV APKTOOL_VERSION=2.8.1
WORKDIR /usr/local/bin
RUN curl -sLO https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool && chmod +x apktool
RUN curl -sL -o apktool.jar https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_${APKTOOL_VERSION}.jar && chmod +x apktool.jar

COPY . /workspace
WORKDIR /workspace
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "-m", "scripts.cli"]
