import sqlite3
from pymongo import MongoClient
from config import Config

#RELACIONAL
def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

#NoRelacional(mongo)
_mongo_client    = MongoClient(Config.MONGO_URI)
db_mongo        = _mongo_client[Config.MONGO_DB]

col_movimientos  = db_mongo["movimientos_log"]
col_sesiones     = db_mongo["sesiones_log"]
col_alertas      = db_mongo["alertas_stock"]
col_facturas_det = db_mongo["facturas_detalle"]


