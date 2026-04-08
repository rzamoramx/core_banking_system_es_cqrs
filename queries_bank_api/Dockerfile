FROM python:3.12-slim
WORKDIR /app

# Install poetry
RUN pip install poetry==2.1.3

# Copy the shared library
COPY libraries/python/com-ivansoft-corebank-lib /app/libraries/python/com-ivansoft-corebank-lib

# Copy the queries bank api component
COPY queries_bank_api /app/queries_bank_api
WORKDIR /app/queries_bank_api

# Configure poetry to not create virtualenvs and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

EXPOSE 8003
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]
