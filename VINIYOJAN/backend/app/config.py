from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'sqlite:///./demo.db'
    jwt_secret: str = 'dev-only-change-me-before-any-deployment'
    cors_origin: str = 'http://localhost:5173'
    vault_dir: str = './vault'
    mock_bank_url: str = 'http://mock-bank:8100'
    enable_scheduler: bool = False
    demo_mode: bool = True
    max_upload_bytes: int = 8 * 1024 * 1024

    @model_validator(mode='after')
    def validate_production(self):
        if not self.demo_mode:
            if len(self.jwt_secret) < 32 or 'dev-only' in self.jwt_secret or 'local-demo' in self.jwt_secret or 'replace-with' in self.jwt_secret:
                raise ValueError('Production requires a strong JWT_SECRET (32+ characters)')
            if self.database_url.startswith('sqlite'):
                raise ValueError('Production requires a configured PostgreSQL database')
        return self

settings = Settings()
