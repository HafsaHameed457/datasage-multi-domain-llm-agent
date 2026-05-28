from langchain_core.tools import Tool
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from sqlalchemy import create_engine, event


def create_sql_tool(domain: str, pg_uri: str, schema: str, llm) -> Tool:
    engine = create_engine(pg_uri)

    @event.listens_for(engine, "connect")
    def set_search_path(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET search_path TO {schema}")
        cursor.close()

    db = SQLDatabase(engine, schema=schema, sample_rows_in_table_info=3)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    query_tool = next(t for t in toolkit.get_tools() if t.name == "sql_db_query")
    query_tool.name = f"sql_{domain}"
    query_tool.description = (
        f"Access the {domain} database (schema: {schema}). "
        f"Use SQL to retrieve structured data about {domain}."
    )
    return query_tool
