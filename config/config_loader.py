import yaml
import os

def load_config(config_path: str = "config/config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    # Override with environment variables if present
    if os.getenv("DATABASE_URL"):
        config["database"]["url"] = os.getenv("DATABASE_URL")
    if os.getenv("SECRET_KEY"):
        config["auth"]["secret_key"] = os.getenv("SECRET_KEY")
    return config