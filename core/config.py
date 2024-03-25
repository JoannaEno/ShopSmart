from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class GlobalConfig(BaseSettings):
  version: str
  docs_url: str
  api_prefix: str
  debug: bool = False
  secret_key: str
  database_url: str
  jwt_secret: str

  class Config:
    env_file = ".env"

settings = GlobalConfig()