import asyncpg

from .model import TransactionRequest


class Database:
    def __init__(self, db_user, db_pw, db_name, db_host, db_port, pool_size):
        self.db_user = db_user
        self.db_pw = db_pw
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port
        self.pool_size = pool_size

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            user=self.db_user,
            password=self.db_pw,
            database=self.db_name,
            host=self.db_host,
            port=int(self.db_port),
            max_size=int(self.pool_size)
        )

    async def save_transaction(self, req: TransactionRequest, client_id: int, t_value: int):
        async with self.pool.acquire() as connection:
            print("Acquired a connection from the pool for SAVE_TRANSACTION")
            async with connection.transaction():
                balance_result = await connection.fetchrow(
                    'SELECT * FROM updateClientBalance($1, $2)',
                    client_id,
                    t_value
                )
                print(balance_result)
                print(f"Balance updated: {balance_result['client_limit']}, {balance_result['new_balance']}")
                await connection.execute(
                    'INSERT INTO transactions (client_id, t_value, t_type, t_description) '
                    'VALUES ($1, $2, $3, $4)',
                    client_id,
                    req.valor,
                    req.tipo,
                    req.descricao
                )
                print("after insert")
                return balance_result['client_limit'], balance_result['new_balance']
    
    async def get_client_statement(self, client_id: int):
        async with self.pool.acquire() as connection:
            print("Acquired a connection from the pool for GET_CLIENT_STATEMENT")
            client_info = await connection.fetchrow(
                'SELECT c_balance, c_limit FROM clients WHERE id = $1',
                client_id
            )

            transactions = await connection.fetch(
                'SELECT t_value, t_type, t_description, created_at '
                'FROM transactions WHERE client_id = $1 '
                'ORDER BY created_at DESC LIMIT 10',
                client_id
            )

            return client_info, transactions

    async def close_pool(self):
        if hasattr(self, 'pool') and self.pool:
            await self.pool.close()