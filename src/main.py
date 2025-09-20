from contextlib import asynccontextmanager
from fastapi import FastAPI, status

from .database import Database
from .model import TransactionRequest
from .service import create_transaction, retrieve_client_statement
from .config import DB_USER, DB_PW, DB_NAME, DB_HOST, DB_PORT, POOL_SIZE


db = Database(
    DB_USER,
    DB_PW,
    DB_NAME,
    DB_HOST,
    DB_PORT,
    POOL_SIZE
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.create_pool()
    print("Database connection pool created successfully")
    yield
    await db.close_pool()
    print("Database connection pool closed")

app = FastAPI(lifespan=lifespan)


@app.post("/clientes/{client_id}/transacoes", status_code=status.HTTP_200_OK)
async def new_transaction(client_id: int, request: TransactionRequest):
    return await create_transaction(client_id, request, db)


@app.get("/clientes/{client_id}/extrato", status_code=status.HTTP_200_OK)
async def get_user_statement(client_id: int):
    return await retrieve_client_statement(client_id, db)
