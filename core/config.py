from pydantic_settings import BaseSettings, SettingsConfigDict

print("Loading config...")
class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env')

    HF_TOKEN:str
    LLM_LOCALHOST_URL:str
    DATASET_URL:str
    EMBEDDING_MODEL:str
    CHAT_COMPLETIONS_MODEL:str
    DB_HOST:str
    DB_PORT:int
    DB_DATABASE:str
    DB_USERNAME:str
    DB_PASSWORD:str
    REDIS_HOST:str
    REDIS_PORT:int
    REDIS_USERNAME:str
    REDIS_PASSWORD:str

settings = Settings()
print("Settings loaded")

