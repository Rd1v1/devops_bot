FROM ubuntu:24.04

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
#ENV DEBIAN_FRONTEND=noninteractive

RUN apt update -y && apt upgrade -y && apt install -y postgresql postgresql-contrib nano openssh-client openssh-server && apt autoremove -y

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=123
ENV POSTGRES_DB=tg_bot

COPY ./pg_hba.conf /etc/postgresql/16/main/pg_hba.conf
COPY ./postgresql.conf /etc/postgresql/16/main/postgresql.conf
#COPY ./init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
EXPOSE 22

COPY ./start.sh /start.sh
RUN chmod +x /start.sh
COPY ./init.sql /init.sql
#CMD ["sh", "-c", "while true; do sleep 1; done"]
CMD /start.sh
