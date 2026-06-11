import json
import os
from dataclasses import dataclass
from typing import ClassVar

base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "secret.json")) as f:
    secret = json.load(f)


@dataclass
class Config:
    db: ClassVar[dict] = {
        "host": secret["DB_HOST"],
        "user": secret["DB_USER"],
        "password": secret["DB_PASSWORD"],
        "charset": secret.get("DB_CHARSET", "utf8mb4"),
        "database": secret["DB_DATABASE"],
    }

    mongo: ClassVar[dict] = {
        "host": secret["MONGO_URI"],
        "collection": secret["MONGO_COLLECTION"],
        "db_name": secret["MONGO_DB_NAME"],
        "default_limit": 5,
    }
