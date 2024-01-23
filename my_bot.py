import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from config_setup import config

# from async_seats import test_request


bot = Bot(token=config["TELEGRAM_TOKEN"])
dp = Dispatcher()


async def on_startup(_):
    print('Running.')


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # res = await test_request()
    await message.answer('hello')


async def main():
    await dp.start_polling(bot, on_startup=on_startup)

if __name__ == "__main__":
    asyncio.run(main())
