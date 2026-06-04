FROM apache/airflow:3.2.1-python3.11

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY pyproject.toml /tmp/pyproject.toml
COPY src /tmp/src

RUN pip install --no-cache-dir \
    "apache-airflow-providers-google>=10.0.0" \
    "apache-airflow-providers-amazon>=8.20.0" \
    "google-cloud-bigquery>=3.25.0" \
    "google-cloud-storage>=2.18.0" \
    "httpx>=0.27.0" \
    "pydantic>=2.7.0" \
    "pydantic-settings>=2.3.0" \
    "structlog>=24.2.0" \
    "boto3>=1.34.0" \
    "pyarrow>=16.0.0" \
    "tenacity>=8.4.0"
