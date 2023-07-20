FROM adoptopenjdk:latest
LABEL VERSION 1.1.0
LABEL MAINTAINER ksg97031 (ksg97031@gmail.com)

ENV APKTOOL_VERSION=2.8.0
RUN apt update && apt install curl python3 -y
RUN alias python=python3
RUN apt install python3-pip -y
RUN alias pip=pip3

WORKDIR /usr/local/bin

RUN curl -sLO https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool && chmod +x apktool
RUN curl -sL -o apktool.jar https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_${APKTOOL_VERSION}.jar && chmod +x apktool.jar

WORKDIR /workspace
RUN pip install frida-gadget

ENTRYPOINT ["bash"]