import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_setup import config

from time import sleep

bot = Bot(token=config["TELEGRAM_TOKEN"])
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # await message.answer("Hello")
    await message.answer("Let's find empty seats!")


@dp.message(Command("2"))
async def cmd_2(message: types.Message):
    await message.answer("?")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
