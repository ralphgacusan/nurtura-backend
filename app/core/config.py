from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ENV: str = "development"

    DB_ENGINE: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @property
    def DATABASE_URL(self):
        return (
            f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
    
    class Config:
        env_file = ".env"

settings = Settings()
