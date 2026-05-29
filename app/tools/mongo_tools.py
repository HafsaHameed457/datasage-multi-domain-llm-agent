from langchain_core.tools import StructuredTool
from pymongo import MongoClient

from app.config import Config


def create_mongo_tool(domain: str, db_name: str, collection_name: str) -> StructuredTool:
    def _search(domain_id: str = None, text_search: str = None) -> str:
        client = MongoClient(Config.MONGO_URI)
        coll = client[db_name][collection_name]
        if domain_id:
            docs = list(coll.find({"domain_id": domain_id}).limit(5))
        elif text_search:
            docs = list(
                coll.find({"text": {"$regex": text_search, "$options": "i"}}).limit(5)
            )
        else:
            return "Provide domain_id or text_search."
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
            f"Use 'domain_id' to look up by ID, or 'text_search' for keyword search."
        ),
    )
