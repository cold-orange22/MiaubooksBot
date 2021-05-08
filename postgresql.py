import asyncpg
from asyncpg.pool import Pool

import config


class Database:
    def __init__(self, pool):
        self.pool: Pool = pool

    @classmethod
    async def create(cls):
        pool = await asyncpg.create_pool(
            user=config.PGUSER,
            password=config.PGPASSWORD,
            host=config.IP,
            database=config.DATABASE
        )
        return cls(pool)

    async def create_table_emails(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Emails (
        id INT NOT NULL,
        user_id INT NOT NULL,
        email VARCHAR(255) NOT NULL,
        datetime VARCHAR(255) NOT NULL,
        PRIMARY KEY (id)
        )
        """
        return await self.pool.execute(sql)

    async def add_email(self, id, user_id, email, datetime):
        sql = "INSERT INTO Emails (id, user_id, email, datetime) VALUES ($1, $2, $3, $4)"
        try:
            return await self.pool.execute(sql, id, user_id, email, datetime)
        except asyncpg.exceptions.UniqueViolationError:
            return "Данный email уже есть в базе данных"

    async def select_all_emails(self):
        sql = "SELECT * FROM Emails"
        return await self.pool.fetch(sql)

    async def count_emails(self):
        sql = "SELECT COUNT(*) FROM Emails"
        return await self.pool.fetchval(sql)

    async def delete_emails(self):
        sql = "DELETE FROM Emails"
        return await self.pool.execute(sql)
