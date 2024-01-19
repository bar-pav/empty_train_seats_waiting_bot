import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from config_setup import config

from async_seats import test_request, show_trains, find_tickets


bot = Bot(token=config["TELEGRAM_TOKEN"])
dp = Dispatcher()

INTERVAL = 10
status = None
wait = False
counter = 0


@dp.message(Command("test"))
async def cmd_start(message: types.Message):
    res = await test_request()
    await message.answer(res)


@dp.message(Command("trains"))
async def cmd_trains(message: types.Message, command: CommandObject):
    """
    args = departure_station, arrival_station, departure_date
    """
    print(command.args.split())
    args = command.args.split()
    args[2] = args[2][0:4] + '-' + args[2][4:6] + '-' + args[2][6:8]
    print(args)
    res = await show_trains(*args)
    await message.answer(res)


@dp.message(Command("wait"))
async def cmd_wait(message: types.Message, command: CommandObject):
    """ :arg:  departure_station, arrival_station, departure_date, train_number=None, tickets_count=None"""

    global wait, status, counter
    wait = True
    started = f"Started at {datetime.now().strftime('%H:%M:%S, %d.%m.%Y')}"
    status = [started, None, None]
    args = command.args.split()
    args[2] = args[2][0:4] + '-' + args[2][4:6] + '-' + args[2][6:8]
    while wait:
        res = await find_tickets(*args, message=message)
        print(res)
        counter += 1
        status[1] = f"Last check at {datetime.now().strftime('%H:%M:%S, %d.%m.%Y')}"
        status[2] = f"Counter: {counter}"
        await asyncio.sleep(INTERVAL)


@dp.message(Command("status"))
async def cmd_status(message: types.Message):
    await message.answer('\n'.join(status) if status else 'Not started')


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    global wait, status, counter
    wait = False
    status = None
    counter = 0
    print('stopped')
    await message.answer('stopped')


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
