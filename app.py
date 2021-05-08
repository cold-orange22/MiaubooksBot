import logging

from aiogram.utils import executor

from loader import dp, db

logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s',
                    level=logging.INFO,
                    )


async def on_startup(dp):
    await db.create_table_emails()


if __name__ == "__main__":  # Это основной файл запуска. Для запуска бота, запустите этот файл.
    import bot
    executor.start_polling(dispatcher=dp, on_startup=on_startup)
