from datetime import timedelta

class Config:
    JWT_SECRET_KEY           = "wamstock-secret-key-2025"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    DATABASE                 = "inventario.db"
    MONGO_URI                = "mongodb+srv://admin:admin@cluster0.fjdxl7l.mongodb.net/?appName=Cluster0"
    MONGO_DB                 = "inventario"
    STOCK_MINIMO             = 5
