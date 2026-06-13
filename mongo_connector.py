from datetime import datetime
from typing import Any
from pymongo import DESCENDING, MongoClient

class MongoDB:
    def __init__(self, mongoconfig: dict) -> None:
        # Connect to MongoDB and immediately verify the connection
        self.client: MongoClient = MongoClient(mongoconfig["host"])
        self.client.admin.command("ping")
        self.collection = self.client[mongoconfig["db_name"]][mongoconfig["collection"]]
        self.default_limit = mongoconfig["default_limit"]

    def log_search(
        self, search_type: str, params: dict, results_count: int
    ) -> None:
        """Saves a search query to the MongoDB collection.

        :param search_type: Query type — "keyword" or "genre_year".
        :param params: Query parameters:
            - keyword:    {"keyword": "matrix"}
            - genre_year: {"genre_id": 5, "genre_name": "Comedy",
                           "year_from": 2000, "year_to": 2010}
        :param results_count: Number of results found.
        """
        self.collection.insert_one({
            "timestamp": datetime.now(),
            "search_type": search_type,
            "params": params,
            "results_count": results_count,
        })

    def get_top_searches(self, limit: int = 0) -> list:
        """Returns the top-N most frequent search queries (aggregation).

        :param limit: Number of records to return.
        """
        if limit == 0:
            limit = self.default_limit
        pipeline: list[dict[str, Any]] = [
            {
                "$group": {
                    "_id": {
                        "search_type": "$search_type",
                        "params": "$params",
                    },
                    "count": {"$sum": 1},
                    "last_searched": {"$max": "$timestamp"},
                    "first_searched": {"$min": "$timestamp"},
                }
            },
            {"$sort": {"count": DESCENDING}},
            {"$limit": limit},
        ]
        return list(self.collection.aggregate(pipeline))

    def get_recent_searches(self, limit: int = 0) -> list:
        """Returns the N most recent search queries by timestamp.

        :param limit: Number of records to return.
        """
        if limit == 0:
            limit = self.default_limit
        return (
            list(
                self.collection
                .find({}, {"_id": 0})
                .sort("timestamp", DESCENDING)
                .limit(limit)
            )
        )

    def __del__(self) -> None:
        """Closes the MongoDB connection when the object is destroyed."""
        self.client.close()
