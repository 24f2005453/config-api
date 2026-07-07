import os
import yaml
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- DEFAULTS ----------------

config = {
    "port": 8000,
    "workers": 1,
    "debug": False,
    "log_level": "info",
    "api_key": "default-secret-000",
}

# ---------------- YAML ----------------

with open("config.development.yaml") as f:
    yaml_cfg = yaml.safe_load(f)

config.update(yaml_cfg)

# ---------------- .ENV ----------------

if os.getenv("APP_PORT"):
    config["port"] = os.getenv("APP_PORT")

if os.getenv("APP_DEBUG"):
    config["debug"] = os.getenv("APP_DEBUG")

if os.getenv("APP_LOG_LEVEL"):
    config["log_level"] = os.getenv("APP_LOG_LEVEL")

if os.getenv("APP_API_KEY"):
    config["api_key"] = os.getenv("APP_API_KEY")

# Alias
if os.getenv("NUM_WORKERS"):
    config["workers"] = os.getenv("NUM_WORKERS")

# ---------------- Simulated OS Environment ----------------

os.environ["APP_PORT"] = "8729"
os.environ["APP_DEBUG"] = "true"
os.environ["APP_LOG_LEVEL"] = "error"
os.environ["APP_API_KEY"] = "key-xwrqx657r3"

config["port"] = os.environ["APP_PORT"]
config["debug"] = os.environ["APP_DEBUG"]
config["log_level"] = os.environ["APP_LOG_LEVEL"]
config["api_key"] = os.environ["APP_API_KEY"]


def to_bool(v):
    return str(v).lower() in ("true", "1", "yes", "on")


@app.get("/effective-config")
def effective_config(set: List[str] = Query(default=[])):

    cfg = dict(config)

    # CLI overrides
    for item in set:
        if "=" not in item:
            continue
        k, v = item.split("=", 1)
        cfg[k] = v

    # Type coercion
    cfg["port"] = int(cfg["port"])
    cfg["workers"] = int(cfg["workers"])
    cfg["debug"] = to_bool(cfg["debug"])
    cfg["log_level"] = str(cfg["log_level"])

    # Mask secret
    cfg["api_key"] = "****"

    return cfg
