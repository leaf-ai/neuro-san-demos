# Deployment

This project is deployed with Docker Compose. The core API and frontend run in the `legal_discovery` service, with supporting databases and caches.

## Port mappings

| Service | Host Port | Container Port | Description |
|---------|-----------|----------------|-------------|
| legal_discovery | 8080 | 5001 | Flask API and web dashboard |
| postgres | 5432 | 5432 | PostgreSQL database |
| neo4j | 7474 / 7687 | 7474 / 7687 | Neo4j HTTP and Bolt ports |
| chromadb | 8000 | 8000 | Chroma vector store |
| redis | 6379 | 6379 | Redis cache and task queue |

## SSL termination

The stack exposes plain HTTP. To serve HTTPS, place a reverse proxy such as Nginx or Traefik in front of the `legal_discovery` service:

1. Terminate TLS at the proxy with certificates from Let's Encrypt or another CA.
2. Forward incoming requests on port 443 to `legal_discovery` on port `8080`.
3. Optionally, redirect port 80 to 443 for all HTTP traffic.

## Environment variables

`docker-compose.yml` reads configuration from environment variables, typically provided via a `.env` file. Key variables include:

- `FLASK_SECRET_KEY`
- `JWT_SECRET`
- `DATABASE_URL` (default `postgresql+psycopg2://postgres@postgres:5432/legal_discovery`, authentication disabled)
- `CHROMA_HOST` / `CHROMA_PORT` (Chroma connects to Postgres without credentials)
- `NEO4J_URI` (Neo4j authentication disabled by default)
- `REDIS_URL`

Adjust these values for your deployment. After updating the `.env` file, rerun `install.sh` to apply changes.
