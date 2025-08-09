FROM python:3.12-bookworm

# Set the working directory
WORKDIR /app

# The uv installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest uv installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the uv installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Copy dependency files first to leverage Docker caching
COPY pyproject.toml uv.lock ./

# Add UV_NO_CACHE=1 to avoid serving a cached broken 404
ENV UV_NO_CACHE=1

# Install dependencies using uv
# RUN uv sync --frozen
# RUN uv sync\
RUN uv sync --frozen || (echo "Frozen sync failed, retrying unlocked..." && uv sync --upgrade)

ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 5000

# Ensure the start script is executable
RUN chmod +x start.sh

# Command to run the application
# CMD ["./start.sh"]
CMD ["bash", "start.sh"]