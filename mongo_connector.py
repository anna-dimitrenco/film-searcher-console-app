from datetime import datetime
from typing import Any

from pymongo import DESCENDING, MongoClient


class MongoDB:
    DB_NAME: str = "ich_edit"          # Имя базы данных MongoDB
    DEFAULT_LIMIT: int = 5             # Лимит по умолчанию для топ-запросов

    def __init__(self, mongoconfig: str, collection_name: str) -> None:
        # Подключаемся к MongoDB и сразу проверяем соединение
        self.client: MongoClient = MongoClient(mongoconfig)
        self.client.admin.command("ping")
        self.collection = self.client[MongoDB.DB_NAME][collection_name]

    def log_search(
        self, search_type: str, params: dict, results_count: int
    ) -> None:
        """Сохраняет поисковый запрос в коллекцию MongoDB.

        :param search_type: Тип запроса — "keyword" или "genre_year".
        :param params: Параметры запроса:
            - keyword:    {"keyword": "matrix"}
            - genre_year: {"genre_id": 5, "genre_name": "Comedy",
                           "year_from": 2000, "year_to": 2010}
        :param results_count: Количество найденных результатов.
        """
        self.collection.insert_one({
            "timestamp": datetime.now(),
            "search_type": search_type,
            "params": params,
            "results_count": results_count,
        })

    def get_top_searches(self, limit: int = DEFAULT_LIMIT) -> list:
        """Возвращает топ-N самых частых поисковых запросов (агрегация).

        :param limit: Количество записей для возврата.
        """
        pipeline: list[dict[str, Any]] = [
            {
                "$group": {
                    "_id": {
                        "search_type": "$search_type",
                        "params": "$params",
                    },
                    "count": {"$sum": 1},
                    "last_searched": {"$max": "$timestamp"},
                }
            },
            {"$sort": {"count": DESCENDING}},
            {"$limit": limit},
        ]
        return list(self.collection.aggregate(pipeline))

    def get_recent_searches(self, limit: int = DEFAULT_LIMIT) -> list:
        """Возвращает N последних поисковых запросов по времени.

        :param limit: Количество записей для возврата.
        """
        return (
            list(
                self.collection
                .find({}, {"_id": 0})
                .sort("timestamp", DESCENDING)
                .limit(limit)
            )
        )

    def __del__(self) -> None:
        """Закрывает соединение с MongoDB при удалении объекта."""
        self.client.close()
