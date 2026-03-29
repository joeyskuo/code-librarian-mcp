from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cl_api_url: str
    cl_api_key: str
    mcp_secret_token: str
    host: str = "0.0.0.0"
    port: int = 8001
    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None
    langfuse_base_url: str | None = None

    model_config = {"env_file": ".env"}


settings = Settings()
