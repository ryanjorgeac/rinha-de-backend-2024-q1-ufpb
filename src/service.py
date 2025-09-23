from datetime import datetime
from asyncpg import CheckViolationError
from fastapi import HTTPException

from .database import Database
from .model import CreateTransactionResponse, TransactionRequest


async def create_transaction(
        client_id: int,
        req: TransactionRequest,
        db: Database
) -> CreateTransactionResponse:
    try:
        t_value = req.valor if req.tipo == 'c' else -req.valor
        limit, balance = await db.save_transaction(req, client_id, t_value)
        return {
            'limite': limit,
            'saldo': balance
        }
    except CheckViolationError:
        raise HTTPException(status_code=422)
    except Exception as e:
        print(e)


async def retrieve_client_statement(client_id: int, db: Database):
    c, ts = await db.get_client_statement(client_id)
    if not c:
        raise HTTPException(status_code=404, detail="Client not found")
    return {
        "saldo": {
            "total": c['c_balance'],
            "data_extrato": datetime.now(),
            "limite": c['c_limit']
        },
        "ultimas_transacoes": [
            {
                "valor": t['t_value'],
                "tipo": t['t_type'],
                "descricao": t['t_description'],
                "realizada_em": t['created_at']
            }
            for t in ts
        ]
    }
