from app.config import load_config


def test_load_config_defaults():
    config = load_config("config/config.example.yaml")
    assert config.subreddits
    assert config.database_path.endswith(".db")
