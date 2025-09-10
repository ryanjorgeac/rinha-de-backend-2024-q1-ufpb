import asyncpg

from model import TransactionRequest


class Database:
    def __init__(self, db_user, db_pw, db_name, db_host, pool_size):
        self.db_user = db_user
        self.db_pw = db_pw
        self.db_name = db_name
        self.db_host = db_host
        self.pool_size = pool_size

    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            user=self.db_user,
            password=self.db_pw,
            database=self.db_name,
            host=self.db_host,
            max_size=int(self.pool_size)
        )

    async def save_transaction(self, req: TransactionRequest, client_id):
        pass

    async def update_client_balance(self, client_id: int, new_value: int):
        pass