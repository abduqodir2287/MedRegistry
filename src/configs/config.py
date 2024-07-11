from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APPLICATION_PORT: str
    APPLICATION_HOST: str
    DOCKER_EXPOSED_PORT: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DATABASE: int
    REDIS_CACHE_EXPIRATION: int
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    LOG_LEVEL: str
    LOG_FORMAT: str
    LOG_FILE: str
    LOG_BACKUP_COUNT: int
    LOG_WRITE_STATUS: bool

# Создайте .env файл и напишите туда свои данные,
# Такие как DB_URL, APPLICATION_PORT и т.д.
# С помощю команды cp env_example .env в Терминале скопируйте в .env файл содержимое в env_example файле

    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:" \
               f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

