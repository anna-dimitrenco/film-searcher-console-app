import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(base_dir, "secret.json")) as f:
    secret = json.load(f)


class Config:
    dbconfig = {
        "host": secret["DB_HOST"],
        "user": secret["DB_USER"],
        "password": secret["DB_PASSWORD"],
        "charset": secret.get("DB_CHARSET", "utf8mb4"),
        "database": secret["DB_DATABASE"],
    }

    mongoconfig = secret["MONGO_URI"]

    collection_name = secret["MONGO_COLLECTION"]
