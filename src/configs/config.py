from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APPLICATION_PORT: str
    APPLICATION_HOST: str
    DOCKER_EXPOSED_PORT: str
    REDIS_HOST: str
    REDIS_PORT: int
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
    REDIS_DISPENSARY: int
    REDIS_ROOM: int
    REDIS_BUNK: int
    REDIS_USERS: int
    REDIS_PATIENTS: int
    ALGORITHM: str
    SECRET_KEY: str


# Создайте .env файл и напишите туда свои данные,
# Такие как DB_URL, APPLICATION_PORT и т.д.
# С помощи команды cp .env_example .env в Терминале скопируйте в .env файл содержимое в .env_example файле

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:" \
               f"{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}/{self.POSTGRES_DB}"

    @property
    def GET_AUTH_DATA(self) -> dict:
        return {"secret_key": self.SECRET_KEY, "algorithm": self.ALGORITHM}


    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

