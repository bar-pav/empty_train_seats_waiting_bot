import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from config_setup import config

from async_seats import test_request, show_trains, main_loop


bot = Bot(token=config["TELEGRAM_TOKEN"])
dp = Dispatcher()

status = None
wait = False


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    res = await test_request()
    await message.answer(res)


@dp.message(Command("trains"))
async def cmd_trains(message: types.Message, command: CommandObject):
    print(command.args.split())
    res = await show_trains(*command.args.split())
    await message.answer(res)


@dp.message(Command("wait"))
async def cmd_wait(message: types.Message, command: CommandObject):
    global wait, status
    wait = True
    status = f"Started at {datetime.now().strftime('%H:%M:%S, %d.%m.%Y')}"
    res = await main_loop(*command.args.split())
    await message.answer(res)


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    global wait, status
    wait = False
    status = None
    await message.answer('stopped')


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
