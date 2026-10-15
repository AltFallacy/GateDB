import os

# DATA_DIR specifies where SQLite databases should be stored.
# Defaults to "." (current working directory) when running locally.
# In Docker/EC2, set to "/app/data" to mount a persistent host volume.
DATA_DIR = os.environ.get("DATA_DIR", ".")
os.makedirs(DATA_DIR, exist_ok=True)

def get_db_path(filename: str) -> str:
    return os.path.join(DATA_DIR, filename)
