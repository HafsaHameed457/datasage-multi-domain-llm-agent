import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    PG_URI = os.getenv("PG_URI")
    MONGO_URI = os.getenv("MONGO_URI")