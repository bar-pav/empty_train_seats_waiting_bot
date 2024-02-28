import asyncio
from datetime import datetime
import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder, KeyboardButton

from config_setup import config
from async_seats import trains, find_tickets


bot = Bot(token=config["TELEGRAM_TOKEN"])
bot.delete_webhook(drop_pending_updates=True)

dp = Dispatcher()

INTERVAL = 10


class SearchStates(StatesGroup):
    trains = State()
    wait = State()


class TrainsCallbackFactory(CallbackData, prefix='train'):
    number: str
    date: str


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
    await message.answer(help_message, parse_mode='html', reply_markup=types.ReplyKeyboardRemove())


async def check_args(args, message, state):
    if args:
        args = args.split()
        print('args: ', args)
        if len(args) == 1 and args[0] in ['отмена', 'выход', 'стоп', 'cancel', 'exit', 'stop']:
            await state.set_state(None)
            return
        if len(args) < 3:
            await message.answer(f"Неверное количество аргументов ({len(args)}).")
            return
        return args


def format_date(date: str) -> str:
    return f'{date[0:4]}-{date[4:6]}-{date[6:8]}'


async def print_trains(args: str, message: types.Message, state: FSMContext):
    args = await check_args(args, message, state)
    if args:
        date = format_date(args[2])
        args[2] = date
        trains_list = await trains(*args)
        trains_list_str = "\n\n".join(str(train) for train in trains_list)
        await message.answer(f"{args[0].capitalize()} - {args[1].capitalize()}:\n\n" + trains_list_str)
    else:
        await message.answer('Введите через пробел станцию отправления, станцию прибытия и дату YYYYMMDD:')


async def start_cycle(args: str, message: types.Message, state: FSMContext):
    args = await check_args(args, message, state)
    if args:
        cycles = (await state.get_data()).get('cycles') or set()
        cycle_id = str(datetime.now())
        cycles.add(cycle_id)
        await state.update_data(cycles=cycles)
        args[2] = format_date(args[2])
        await state.set_state(None)
        try:
            while cycle_id in (await state.get_data()).get('cycles'):
                tickets = await find_tickets(*args)
                if tickets:
                    print(tickets)
                    await message.answer(tickets)
                await asyncio.sleep(INTERVAL)
            else:
                await message.answer(str(cycle_id) + ' stopped')
        except:
            print("EXCEPTION IN WAIT CYCLE.")
    else:
        await message.answer("Введите через пробел станцию отправления, станцию прибытия, дату YYYYMMDD, номер поезда и количество билетов:")


@dp.message(Command("status"))
async def cmd_status(message: types.Message, state: FSMContext):
    current_state = str((await state.get_state()) or '')
    if (await state.get_data()).get('cycles'):
        await message.answer(f"{current_state}\nЗапущенные циклы: \n" + '\n'.join((await state.get_data()).get('cycles')))
    else:
        await message.answer(f"{current_state}\nНет запущенных циклов.")


@dp.message(Command("stop"))
async def cmd_stop(message: types.Message, state: FSMContext):
    await state.clear()
    await state.update_data(cycles=set())
    print('Stopped')
    await message.answer('Stopped')


@dp.message(StateFilter(None), Command("trains"))
async def cmd_trains(message: types.Message, command: CommandObject, state: FSMContext):
    """
    args = departure_station, arrival_station, departure_date
    """
    await state.set_state(SearchStates.trains)
    await print_trains(command.args, message, state)


@dp.message(StateFilter(SearchStates.trains))
async def trains_state(message: types.Message, state: FSMContext):
    await print_trains(message.text, message, state)
    await state.set_state(None)


@dp.message(StateFilter(None), Command("wait"))
async def cmd_wait(message: types.Message, command: CommandObject, state: FSMContext):
    """ :arg:  departure_station, arrival_station, departure_date, train_number=None, tickets_count=None"""
    await state.set_state(SearchStates.wait)
    await start_cycle(command.args, message, state)


@dp.message(StateFilter(SearchStates.wait))
async def wait_state(message: types.Message, state: FSMContext):
    await start_cycle(message.text, message, state)



# ------------------------------------------TEST---------------------------------
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
# ---------------------------------------------------------------------------


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    asyncio.run(main())
