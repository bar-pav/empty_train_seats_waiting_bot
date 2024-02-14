import asyncio
from datetime import datetime
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config_setup import config
from async_seats import test_request, show_trains, find_tickets


bot = Bot(token=config["TELEGRAM_TOKEN"])
dp = Dispatcher()

INTERVAL = 10


class WaitSeats(StatesGroup):
    wait = State()


help_message = """
    <b>/trains &lt;станция отправления&gt; &lt;станция прибытия&gt; &lt;дата в формате YYYYMMDD&gt;</b> - печатает 
    список поездов по заданному направлению на указанную дату.\n
"""


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    # await message.delete()
    await message.answer(help_message, parse_mode='html')


@dp.message(Command("test"))
async def cmd_start(message: types.Message):
    # res = await test_request()
    await message.answer('hello')


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


@dp.message(StateFilter(None), Command("wait"))
async def cmd_wait(message: types.Message, command: CommandObject, state: FSMContext):
    """ :arg:  departure_station, arrival_station, departure_date, train_number=None, tickets_count=None"""

    await state.set_state(WaitSeats.wait)
    started = f"Started at {datetime.now().strftime('%H:%M:%S, %d.%m.%Y')}"
    status = [started, None, None]
    await state.update_data(wait=True)
    args = command.args.split()
    args[2] = args[2][0:4] + '-' + args[2][4:6] + '-' + args[2][6:8]
    counter = 0
    while (await state.get_data()).get('wait'):
        # res = await find_tickets(*args, message=message)
        res = await find_tickets(*args)
        # print(res)
        counter += 1
        status[1] = f"Last check at {datetime.now().strftime('%H:%M:%S, %d.%m.%Y')}"
        status[2] = f"Counter: {counter}"
        await state.update_data(status=status)
        # print(status)
        await asyncio.sleep(INTERVAL)


@dp.message(Command("status"))
async def cmd_status(message: types.Message, state: FSMContext):
    print(state)
    if (await state.get_state()) == "WaitSeats:wait":
        print((await state.get_data()).get("status"))
        await message.answer(str((await state.get_data()).get("status")))
    # await message.answer('\n'.join(status) if status else 'Not started')


@dp.message(WaitSeats.wait, Command("stop"))
async def cmd_stop(message: types.Message, state: FSMContext):
    await state.clear()
    print('stopped')
    await message.answer('stopped')


@dp.message(Command('inline'))
async def cmd_inline(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text='get random value', callback_data='random'))
    await message.answer('Inline kb', reply_markup=kb.as_markup())


@dp.callback_query(F.data == 'random')
async def cmd_random(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.row(types.InlineKeyboardButton(text='get random value', callback_data='random'))
    await callback.message.edit_text(f'{random.randint(1, 10)}', reply_markup=kb.as_markup())
    await callback.answer()


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
