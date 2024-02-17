import asyncio
from datetime import datetime
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardMarkup, ReplyKeyboardBuilder, KeyboardButton

from config_setup import config
from async_seats import test_request, show_trains, find_tickets


from time import sleep

bot = Bot(token=config["TELEGRAM_TOKEN"])
dp = Dispatcher()

INTERVAL = 10


class WaitSeats(StatesGroup):
    wait = State()


help_message = """
<b>/trains &lt;станция А&gt; &lt;станция Б&gt; &lt;дата YYYYMMDD&gt;</b> - \
    печатает список поездов по заданному направлению на указанную дату.
    
<b>/wait &lt;станция А&gt; &lt;станция Б&gt; &lt;дата YYYYMMDD&gt; &lt;№ поезда&gt; &lt;количество билетов&gt;</b> - \
    ожидать появление необходимого количества билетов на указанный поезд. При появлении билета придет сообщение.
    
<b>/status</b> - выводит статус процесса ожидания.
"""


b1 = KeyboardButton(text='/help')
b2 = KeyboardButton(text='/status')
kb = ReplyKeyboardBuilder()
kb.add(b1)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer('start', reply_markup=kb.as_markup(resize_keyboard=True, one_time_keyboard=True))


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    # await message.delete()
    await message.answer(help_message, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())


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
    cycles = (await state.get_data()).get('cycles') or set()
    cycle_id = datetime.now()
    cycles.add(cycle_id)
    await state.update_data(cycles=cycles)
    started = f"Start: {datetime.now().strftime('%H:%M:%S, %d.%m.%Y')}"
    status = [started, None, None]
    args = command.args.split()
    args[2] = args[2][0:4] + '-' + args[2][4:6] + '-' + args[2][6:8]
    counter = 0
    while cycle_id in (await state.get_data()).get('cycles'):
        """ Обернуть цикл в функцию.
            Поместить цикл с флагом в словарь (ключ - функция, значение - флаг работы цикла) и добавить словарь в текущее состояние FSM.
            При появлении нового цикла, он проверяет наличие других циклов и при их наличии переводит их флаги в значение False."""
        # res = await find_tickets(*args, message=message)
        res = await find_tickets(*args)
        # print(res)

        counter += 1
        status[1] = f"Last check: {datetime.now().strftime('%H:%M:%S, %d.%m.%Y')}"
        status[2] = f"Counter: {counter}"
        await state.update_data(status=status)
        if res:
            print(res)
            await message.answer(res)
        await asyncio.sleep(INTERVAL)
    else:
        await message.answer(str(cycle_id) + ' stopped')


@dp.message(Command("status"))
async def cmd_status(message: types.Message, state: FSMContext):
    print(state)
    if (await state.get_state()) == "WaitSeats:wait":
        print((await state.get_data()).get("status"))
        await message.answer("\n".join((await state.get_data()).get("status")))
    else:
        await message.answer('В данный момент поиск билетов не запущен. Запустите командой wait.')


@dp.message(WaitSeats.wait, Command("stop"))
async def cmd_stop(message: types.Message, state: FSMContext):
    await state.clear()
    await state.update_data(cycles=set())
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
