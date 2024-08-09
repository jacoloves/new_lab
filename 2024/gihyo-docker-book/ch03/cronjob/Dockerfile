FROM ubuntu:23.10

RUN apt update
RUN apt install -y cron

COPY task.sh /usr/local/bin
COPY cron-example /etc/cron.d/
RUN chmod 0644 /etc/cron.d/cron-example

CMD [ "cron", "-f" ]
