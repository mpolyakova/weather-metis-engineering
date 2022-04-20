FROM postgres:latest

RUN apt-get update
RUN apt-get -y install python python3-pip

RUN pip install \
    dagster \
    dagster-graphql \
    dagit \
    dagster-postgres \
    dagster-docker

RUN mkdir -p /opt/dagster/dagster_home /opt/dagster/app

ENV DAGSTER_HOME=/opt/dagster/dagster_home/
ENV POSTGRES_PASSWORD=test
COPY entrypoint.sh /usr/local/bin/
COPY dagster.yaml /opt/dagster/dagster_home/
WORKDIR /opt/dagster/app

RUN apt-get install -y libpq-dev
RUN pip install psycopg2 requests numpy pandas python-dotenv streamlit matplotlib pyaml
EXPOSE 3000
EXPOSE 8501
EXPOSE 8000

ENTRYPOINT ["entrypoint.sh"]


