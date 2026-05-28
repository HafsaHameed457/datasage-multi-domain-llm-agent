import json

from langchain_core.tools import Tool
from pymongo import MongoClient

from app.config import Config


def create_mongo_tool(domain: str, db_name: str, collection_name: str) -> Tool:
    def _search(query_json: str) -> str:
        client = MongoClient(Config.MONGO_URI)
        coll = client[db_name][collection_name]
        try:
            filters = json.loads(query_json)
        except json.JSONDecodeError:
            return "Invalid JSON. Use {'domain_id': 123} or {'text_search': 'keyword'}."
        if "domain_id" in filters:
            docs = list(coll.find({"domain_id": str(filters["domain_id"])}).limit(5))
        elif "text_search" in filters:
            regex = filters["text_search"]
            docs = list(coll.find({"text": {"$regex": regex, "$options": "i"}}).limit(5))
        else:
            return "Unsupported query. Use 'domain_id' or 'text_search'."
        results = [
            {"text": d.get("text", "")[:500], "sentiment": d.get("sentiment")}
            for d in docs
        ]
        return json.dumps(results, ensure_ascii=False)

    return Tool(
        name=f"mongo_{domain}",
        description=(
            f"Search {domain} text data in MongoDB. "
            f"Input a JSON string: "
            f"{{'domain_id': 123}} to fetch documents by ID, "
            f"or {{'text_search': 'keyword'}} to search inside text fields."
        ),
        func=_search,
    )
