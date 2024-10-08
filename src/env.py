from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Env(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )
    ENV_MODE: Optional[str] = 'dev'
    AZURE_DEVOPS_ORGANIZATION: str
    AZURE_DEVOPS_PROJECT: str
    AZURE_DEVOPS_PAT: str

    API_KEY: str
    LANGSMITH_API_KEY: str
    LANGCHAIN_TRACING_V2: bool
    LANGCHAIN_ENDPOINT: str
    LANGCHAIN_API_KEY: str
    LANGCHAIN_PROJECT: str


env = Env()
