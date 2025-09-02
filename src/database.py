import asyncpg


class Database:
    async def __init__(self, db_user, db_pw, db_name, db_host, pool_size):
        self.pool = await asyncpg.create_pool(
            user=db_user,
            password=db_pw,
            database=db_name,
            host=db_host,
            max_size=int(pool_size)
        )

    