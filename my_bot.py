import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_setup import config

bot = Bot(token=config["TELEGRAM_TOKEN"])
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
