from langchain_core.tools import Tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine, event


TOOL_MAP = {
    "sql_db_query": "query",
    "sql_db_schema": "schema",
    "sql_db_list_tables": "list_tables",
}


def create_sql_tools(domain: str, pg_uri: str, schema: str, llm) -> list[Tool]:
    engine = create_engine(pg_uri)

    @event.listens_for(engine, "connect")
    def set_search_path(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET search_path TO {schema}")
        cursor.close()

    db = SQLDatabase(engine, schema=schema, sample_rows_in_table_info=3)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    domain_tools = []
    for tool in toolkit.get_tools():
        suffix = TOOL_MAP.get(tool.name)
        if suffix:
            tool.name = f"sql_{domain}_{suffix}"
            tool.description = (
                f"[{domain}] {tool.description}. "
                f"Schema: {schema}. "
                f"Table prefix: {schema}."
            )
            domain_tools.append(tool)

    return domain_tools
