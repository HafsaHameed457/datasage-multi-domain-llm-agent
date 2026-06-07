import re

from langchain_core.tools import StructuredTool
from pymongo import MongoClient

from app.config import Config


def _parse_query(query: str) -> dict:
    query = query.strip()
    if query.isdigit():
        return {"domain_id": query}
    return {"text_search": query}


def create_mongo_tool(domain: str, db_name: str, collection_name: str) -> StructuredTool:
    def _search(query: str) -> str:
        client = MongoClient(Config.MONGO_URI)
        coll = client[db_name][collection_name]
        params = _parse_query(query)
        if "domain_id" in params:
            docs = list(coll.find({"domain_id": params["domain_id"]}).limit(5))
        else:
            docs = list(
                coll.find({"text": {"$regex": params["text_search"], "$options": "i"}}).limit(5)
            )
        results = [
            f"text: {d.get('text', '')[:500]}\nsentiment: {d.get('sentiment')}"
            for d in docs
        ]
        return "\n---\n".join(results) if results else "No results found."

    return StructuredTool.from_function(
        func=_search,
        name=f"mongo_{domain}",
        description=(
            f"Search {domain} text data (reviews/lyrics) in MongoDB. "
            f"Pass a single query string — a number to look up by ID, "
            f"or keywords to search the text field."
        ),
    )
