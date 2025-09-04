from asyncpg import CheckViolationError
from fastapi import HTTPException

from database import Database
from model import CreateTransactionResponse, TransactionRequest


async def create_transaction(
        client_id: int,
        req: TransactionRequest,
        db: Database
) -> CreateTransactionResponse:
    try:
        t_value = req.valor if req.tipo == 'c' else -req.valor
        await db.save_transaction(client_id, req)

        client = await db.increment_client_balance(client_id, t_value)
        return {
            'limite': client['limite'],
            'saldo': client['saldo']
        }
    except CheckViolationError:
        raise HTTPException(status_code=422)
    except Exception as e:
        print(e)


async def retrieve_client_statement(client_id: int, db: Database):
    pass
