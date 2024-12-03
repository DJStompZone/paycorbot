
# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables for Poetry installation
ENV POETRY_VERSION=1.5.1
ENV POETRY_HOME=/opt/poetry
ENV PATH=$POETRY_HOME/bin:$PATH

# Install Poetry
RUN apt-get update && apt-get install -y curl && \
    curl -sSL https://install.python-poetry.org | python3 -

# Set the working directory in the container
WORKDIR /app

# Copy only the pyproject.toml and poetry.lock first (to leverage Docker caching)
COPY pyproject.toml poetry.lock* /app/

# Install dependencies
RUN poetry install --no-root --only main

# Copy the rest of the application
COPY . /app

# Set the default command to run the application
CMD ["poetry", "run", "python", "-m", "paycorbot"]
