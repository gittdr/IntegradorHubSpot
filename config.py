import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Hubspot
    API_TOKEN = os.getenv("API_TOKEN")
    API_URL = os.getenv("API_URL")
    API_DEALS_ENDPOINT = os.getenv("API_DEALS_ENDPOINT")
    API_DEALS_PARAMS = os.getenv("API_DEALS_PARAMS")
    API_OWNERS_ENDPOINT = os.getenv("API_OWNERS_ENDPOINT")
    API_OWNERS_PARAMS = os.getenv("API_OWNERS_PARAMS")
    API_PIPELINES_ENDPOINT = os.getenv("API_PIPELINES_ENDPOINT")
    API_PARAMS2 = os.getenv("API_PARAMS2")

    # Base de Datos
    BD_DRIVER = os.getenv("BD_DRIVER")
    BD_SERVER = os.getenv("bd_server")
    BD_DATABASE = os.getenv("bd_database")
    BD_USERNAME = os.getenv("bd_username")
    BD_PASSWORD = os.getenv("bd_password")

    # Queries SQL
    QUERY_INSERT_DEAL = os.getenv("QUERY_INSERT_DEAL")
    QUERY_INSERT_OBJECTS = os.getenv("QUERY_INSERT_OBJECTS")