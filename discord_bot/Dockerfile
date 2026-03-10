FROM python:3.12-slim

WORKDIR /srv/FunnelAgent

# Install git for auto-update
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install claude-agent-sdk (bundles CLI internally)
RUN pip install claude-agent-sdk

# Copy and install requirements
COPY discord_bot/requirements.txt discord_bot/requirements.txt
COPY scripts/requirements.txt scripts/requirements.txt
RUN pip install -r discord_bot/requirements.txt -r scripts/requirements.txt

# Copy application code
COPY . .

# Create non-root user and ensure writable dirs
RUN useradd -m -u 1000 agent && chown -R agent:agent /srv/FunnelAgent
RUN mkdir -p /srv/FunnelAgent/discord_bot/logs /srv/FunnelAgent/discord_bot/data /srv/FunnelAgent/output && \
    chown -R agent:agent /srv/FunnelAgent/discord_bot/logs /srv/FunnelAgent/discord_bot/data /srv/FunnelAgent/output
USER agent

# Persistent volumes for output and database
VOLUME ["/srv/FunnelAgent/output", "/srv/FunnelAgent/discord_bot/data"]

ENTRYPOINT ["python", "-m", "discord_bot.app.main"]
