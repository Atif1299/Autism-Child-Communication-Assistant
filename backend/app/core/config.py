from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Supportive Communication Agent"
    
    # API settings
    API_V1_STR: str = "/api/v1"

    # Database settings
    DATABASE_URL: str = "postgresql://:@localhost/dbname"

    # OpenAI API Key
    OPENAI_API_KEY: str = "your_api_key_here"

    class Config:
        env_file = ".env"

settings = Settings()
