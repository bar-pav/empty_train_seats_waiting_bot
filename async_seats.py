from datetime import datetime, timedelta
from collections import namedtuple
from bs4 import BeautifulSoup as bs
import asyncio
import aiohttp

from config_setup import config

telegram_token = config['TELEGRAM_TOKEN']
my_telegram_id = config['my_telegram_id']


Train = namedtuple('Train', ['number', 'route', 'time', 'tickets'])


def get_rw_url(from_, to_, date):
    return f"https://pass.rw.by/ru/route/?from={from_}&to={to_}&date={date}"


def parse_response(page):
    """
    :param page: страница с сайта pass.rw.by.
    :return: (list[Train], 'empty_seats_count': int)
    """
    empty_seats_count = 0
    trains_list = []
    page_bs = bs(page, features="html.parser")
    train_blocks = page_bs.css.select('div[data-train-info]')
    for train_block in train_blocks:
        train_info = {}
        train_number = train_block.find('span', attrs={'class': 'train-number'}).text.strip()
        train_route = train_block.find('span', attrs={'class': 'train-route'}).text.strip().split('\xa0— ')
        train_info['route'] = train_route
        train_from_time = train_block.find('div', attrs={'class': 'sch-table__time train-from-time'}).text.strip()
        train_to_time = train_block.find('div', attrs={'class': 'sch-table__time train-to-time'}).text.strip()
        train_duration_time = train_block.find('div',
                                               attrs={'class': 'sch-table__duration train-duration-time'}).text.strip()
        train_time = (train_from_time, train_to_time, train_duration_time)
        train_info['time'] = train_time
        tickets = []
        tickets_block = train_block.find('div', attrs={'class': 'sch-table__cell cell-4'})
        if tickets_block:
            ticket_quants = tickets_block.find_all('div', attrs={'class': "sch-table__t-item has-quant"})
            for ticket_info in ticket_quants:
                ticket_name = ticket_info.find('div', attrs={'class': "sch-table__t-name"}).text.strip()
                ticket_quant = ticket_info.find('a', attrs={'class': "sch-table__t-quant"}).find('span').text.strip()
                empty_seats_count += int(ticket_quant)
                ticket_cost = ticket_info.find('span', attrs={'class': "ticket-cost"}).text.strip()
                tickets.append((ticket_name, ticket_quant, ticket_cost))
        if train_number:
            trains_list.append(Train(train_number, train_route, train_time, tickets))
    return trains_list, empty_seats_count


def trains_brief_info(trains) -> str:
    res = ''
    for train in trains:
        tickets_count = '\n\t\t'.join([f'{tickets[1]} по {tickets[2]}' for tickets in train.tickets])
        res += (f'<b>{train.number}</b>: {train.route[0]} - {train.route[1]}({train.time[0]}-{train.time[1]}) '
                f'\n\tБилеты:\n\t\t'
                f'{tickets_count}') + '\n\n'
    return res


def has_tickets(tickets_count):
    def check(train):
        seats_count = 0
        for seats in train.tickets:
            seats_count += int(seats[1])
        if seats_count >= int(tickets_count):
            return True
    return check


def filter_tickets(trains, train_number=None, tickets_count=None):
    if not tickets_count and not train_number:
        return list(filter(lambda t: t.tickets, trains))
    if train_number and not tickets_count:
        return list(filter(lambda t: t.number == train_number and t.tickets, trains))
    if not train_number and tickets_count:
        return list(filter(has_tickets(tickets_count), trains))
    if train_number and tickets_count:
        return list(filter(lambda t: t.number == train_number and has_tickets(tickets_count)(t), trains))


async def get_webpage(rw_url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(rw_url) as response:
                if response.status == 200:
                    return await response.text()
    except aiohttp.ClientConnectionError as exc:
        print(exc)
        return ''


async def find_tickets(departure_station,
                       arrival_station,
                       departure_date,
                       train_number=None,
                       tickets_count=None,
                       message=None):
    url = get_rw_url(departure_station, arrival_station, departure_date)
    page = await get_webpage(url)
    trains, empty_seats_count = parse_response(page)
    tickets_filtered = filter_tickets(trains, train_number=train_number, tickets_count=tickets_count)
    # print(tickets_filtered)
    # if message and tickets_filtered:
    #     print(trains_brief_info(tickets_filtered))
    #     # await message.answer(show_brief_info(tickets_filtered))
    return trains_brief_info(tickets_filtered)


async def main_loop(departure_station, arrival_station, departure_date, train_number=None, tickets_count=None):
    while True:
        res = await find_tickets(departure_station, arrival_station, departure_date, train_number, tickets_count)
        await asyncio.sleep(10)
        print(res)
        return res


async def test_request():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    url = get_rw_url('Минск', 'Витебск', tomorrow)
    page = await get_webpage(url)
    if page:
        trains, seats_count = parse_response(page)
        print(trains)
        # print(trains['empty_seats_count'])
        # print('Количество поездов = ', len(trains['trains']))
        print('Количество поездов = ', len(trains))
        print('found_tickets:')
        t = list(filter_tickets(trains, train_number=None, tickets_count=None))
        print(t)
        print(trains_brief_info(t))
        # return show_brief_info(query_tickets(trains, train_number=None, tickets_count=None))
        # print('show_trains', show_trains(trains))
    else:
        print('No page. Check request parameters.')


async def get_trains(from_, to_, date):
    url = get_rw_url(from_, to_, date)
    page = await get_webpage(url)
    trains, _ = parse_response(page)
    return trains


if __name__ == "__main__":
    asyncio.run(test_request())

    # main_loop('Минск', 'Витебск', '2023-11-26')
