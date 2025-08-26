import os
from dotenv import load_dotenv

# Load environment variables from .env in project root if present
load_dotenv()

# Application secrets
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "")

# Database and service configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres@postgres:5432/legal_discovery",
)
CHROMA_HOST = os.getenv("CHROMA_HOST", "chromadb")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# Model configuration
EMBED_MODEL = os.getenv(
    "EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
CROSS_ENCODER_MODEL = os.getenv(
    "CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
)
