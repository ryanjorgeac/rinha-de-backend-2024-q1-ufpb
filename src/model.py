from datetime import datetime

from asyncpg import Record
from pydantic import BaseModel, Field
from typing import Literal


class TransactionRequest(BaseModel):
    valor: int
    tipo: Literal['c', 'd']
    descricao: str = Field(min_length=1, max_length=10)


class TransactionModel(TransactionRequest):
    date: datetime


class CreateTransactionResponse(BaseModel):
    limite: int
    saldo: int
