FROM ubuntu:23.10

ENV TZ=Asia/Tokyo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt update
RUN apt -y install \
    mycli redis-tools \
    iputils-ping net-tools dnsutils telnet tcpdump traceroute

CMD [ "/bin/bash" ]