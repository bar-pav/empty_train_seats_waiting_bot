import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_setup import config

from async_seats import test_request


bot = Bot(token=config["TELEGRAM_TOKEN"])
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Ну, подожди ты!")
    res = await test_request()
    await message.answer(res)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
