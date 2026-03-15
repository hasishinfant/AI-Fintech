"""Application configuration"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/intellicredit"

    # AWS
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: str = "intellicredit-documents"

    # API Keys
    OPENAI_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    CIBIL_API_KEY: str = ""

    # Security
    SECRET_KEY: str = "your-secret-key-must-be-at-least-thirty-two-characters-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External APIs
    MCA_API_URL: str = "https://mca.gov.in/api"
    ECOURTS_API_URL: str = "https://ecourts.gov.in/api"
    RBI_API_URL: str = "https://rbi.org.in/api"

    # Base Rate
    BASE_INTEREST_RATE: float = 8.5

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


settings = Settings()
