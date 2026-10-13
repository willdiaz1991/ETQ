import os

from dotenv import load_dotenv

from infrastructure.logging.LoggerImplements import LoggerImplements

logger = LoggerImplements("ConfigLogger")


class Config:
    def __init__(self):
        """
        Environment configuration.

        👉 Default: assumes production (reads from system environment variables).
        ✅ For local development: uncomment the section below to load variables from a `.env` file.
        """
        logger.log_information("Using system environment variables", method="Config.__init__")

        # 👇 UNCOMMENT THIS SECTION FOR LOCAL DEVELOPMENT (.env support)
        base_path = os.path.dirname(os.path.abspath(__file__))
        env_file = os.path.join(base_path, f"../.env.dev")

        if os.path.exists(env_file):
            load_dotenv(env_file)
            logger.log_information(f"Environment file loaded successfully: {env_file}", method="Config.__init__")
        else:
            logger.log_information("Optional .env.dev file not present; using system environment variables.", method="Config.__init__")

    def get(self, key: str):
        """Get the value of an environment variable."""
        value = os.getenv(key)
        if value is not None:
            logger.log_information(f"Environment variable loaded: {key}", method="Config.get")
        else:
            logger.log_warning(f"Environment variable {key} is not defined.", method="Config.get")
        return value
