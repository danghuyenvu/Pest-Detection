from fastapi import FastAPI
from api.routes import predict, history, stats
from db.database import engine, Base
from models.detection import Detection
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(predict.router)
app.include_router(history.router)
app.include_router(stats.router)