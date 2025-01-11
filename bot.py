import config
import asyncio
import logging
from aiogram import Bot, Dispatcher
import default, testprocess
from aiogram.client.default import DefaultBotProperties

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token=config.token, default=DefaultBotProperties(parse_mode='HTML'))
# Диспетчер
dp = Dispatcher()
# Связь диспетчера и роутеров (связь диспетчер — роутеры — хэндлеры)
dp.include_routers(default.default_router, testprocess.tpr)


# Запуск процесса поллинга новых апдейтов
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
