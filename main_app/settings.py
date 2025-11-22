import pathlib

from pydantic import Field, NonNegativeInt, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    FILES_ROOT: pathlib.Path = Field(default=pathlib.Path("/data_files_storage"), alias="FILES_ROOT")
    IMAGES_TTL_HOURS: NonNegativeInt = Field(default=1, alias="IMAGES_TTL_HOURS")
    PDF_TTL_HOURS: NonNegativeInt = Field(default=24, alias="PDF_TTL_HOURS")
    CHECK_INTERVAL_SECONDS: PositiveInt = Field(default=600, alias="CHECK_INTERVAL_SECONDS")

    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    oneshot: bool = Field(default=False, alias="ONESHOT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def images_ttl_seconds(self) -> int:
        return int(self.images_ttl_hours) * 3600

    @property
    def pdf_ttl_seconds(self) -> int:
        return int(self.pdf_ttl_hours) * 3600


settings = Settings()
