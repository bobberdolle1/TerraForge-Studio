FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libspatialindex-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Install the project itself
RUN poetry install --no-interaction --no-ansi

# Expose FastAPI port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "realworldmapgen.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
