from datetime import datetime
import time
from bs4 import BeautifulSoup as bs
import requests

import asyncio
import aiohttp

from config_setup import config

telegram_token = config['TELEGRAM_TOKEN']
my_telegram_id = config['my_telegram_id']


def get_departure_station():
    return input("Введите станцию отправления.").strip()


def get_arrival_station():
    return input("Введите станцию назначения.").strip()


route = ('Витебск', 'Минск-Пассажирский')
# departure_station = get_departure_station()
# arrival_station = get_arrival_station()


# --------------------------------------------------------------


def get_departure_date():
    return input("Введите дату отправления в формате dd.mm.yyyy.").strip()


# departure_date = get_departure_date().split('.')
# departure_date = {
#     'day': departure_date[0],
#     'month': departure_date[1],
#     'year': departure_date[2]
# }
#
# if isinstance(departure_date, dict):
#     departure_date = f"{departure_date['year']}-{departure_date['month']}-{departure_date['day']}"
# else:
#     departure_date = input("Enter departure date in format 'YYYY-MM-DD' (YEAR-MONTH-DAY):\n")

# print(f"Enter departure station (1 - Vitebsk) (2 - Minsk):")
# dep = input("\tStation: ")
# if dep == '1' or dep == 'Vitebsk':
#     route_from, route_to = route
# else:
#     route_from, route_to = route[::-1]

telegram_url = "https://api.telegram.org/bot" + telegram_token + '/sendMessage' + '?chat_id=' + my_telegram_id + '&text='


def send_msg(text):
    url = telegram_url + text
    result = requests.get(url)
    print(result.json())


def test_get_updates_from_bot():
    url = "https://api.telegram.org/bot" + telegram_token + '/getUpdates'
    result = requests.get(url)
    print(result.json())


def get_rw_url(from_, to_, date):
    return f"https://pass.rw.by/ru/route/?from={from_}&to={to_}&date={date}"


def check_attribute(tag):
    if 'data-train-info' in tag.attrs:
        return True


def parse_response(response):
    """

    :param response:
    :return: dict 'trains' with keys:
        {
            'trains':
                {
                    'route': str,
                    'time': ('departure', 'arrival', 'duration'),
                    'tickets': [('name', 'quantity', 'cost'), (...)],
                },
            'empty_seats_count': int,
        }
    """
    empty_seats_count = 0
    trains = {}
    page = bs(response, features="html.parser")
    train_blocks = page.css.select('div[data-train-info]')
    # train_table = page.find('div', attrs={'class': 'sch-table__body js-sort-body'})
    # train_blocks = train_table.find_all('div', recursive=False)
    # train_blocks = filter(check_attribute, train_blocks)
    trains['trains'] = {}
    for train_block in train_blocks:
        train_info = {}
        train_number = train_block.find('span', attrs={'class': 'train-number'}).text.strip()
        train_route = train_block.find('span', attrs={'class': 'train-route'}).text.strip().replace('\xa0', ' ')
        train_from_time = train_block.find('div', attrs={'class': 'sch-table__time train-from-time'}).text.strip()
        train_to_time = train_block.find('div', attrs={'class': 'sch-table__time train-to-time'}).text.strip()
        train_duration_time = train_block.find('div', attrs={'class': 'sch-table__duration train-duration-time'}).text.strip()
        train_info['route'] = train_route
        train_info['time'] = (train_from_time, train_to_time, train_duration_time)
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
        train_info['tickets'] = tickets
        if train_number:
            trains['trains'][train_number] = train_info
    trains['empty_seats_count'] = empty_seats_count
    return trains


def show_brief_info(trains):
    for train, train_info in trains.items():
        tickets_count = '\n\t\t'.join([f'{tickets[1]} за {tickets[2]}' for tickets in train_info['tickets']])
        return (f'{train} ({train_info["route"]}) {train_info["time"][0]}-{train_info["time"][1]} \n\tБилеты:\n\t\t '
                f'{tickets_count}')


def has_tickets(tickets_count):
    def check(train_tuple):
        seats_count = 0
        for seats in train_tuple[1]['tickets']:
            seats_count += int(seats[1])
        if seats_count >= tickets_count:
            return True
    return check


def query_tickets(trains, train_number=None, tickets_count=None):
    if not tickets_count and not train_number:
        return dict(filter(lambda t: t[1]['tickets'], trains['trains'].items()))
    if train_number and not tickets_count:
        return dict(filter(lambda t: t[0] == train_number and t[1]['tickets'], trains['trains'].items()))
    if not train_number and tickets_count:
        return dict(filter(has_tickets(tickets_count), trains['trains'].items()))
    if train_number and tickets_count:
        return dict(filter(lambda t: t[0] == train_number and has_tickets(tickets_count)(t), trains['trains'].items()))


async def get_webpage(rw_url):
    start_response = datetime.now()
    session = aiohttp.ClientSession()
    async with session.get(rw_url) as response:
        if response.status == 200:
            end_response = datetime.now()
            trains = parse_response(await response.text())
            end_parse = datetime.now()
            print("Full time:", end_parse - start_response, 's')
            print("\tResponse time:", end_response - start_response, 's')
            print("\tParse time:", end_parse - end_response, 's')
    await session.close()
    return trains


async def find_tickets(departure_station, arrival_station, departure_date, train_number=None, tickets_count=None):
    url = get_rw_url(departure_station, arrival_station, departure_date)
    trains = await get_webpage(url)
    result = query_tickets(trains, train_number=train_number, tickets_count=tickets_count)
    show_brief_info(result)


def main_loop(departure_station, arrival_station, departure_date, train_number=None, tickets_count=None):
    while True:
        # with open('departure_date.txt', 'rt') as f:
        #     dep_date_from_file = f.read().strip()
        # if dep_date_from_file:
        #     departure_date = dep_date_from_file
        find_tickets(departure_station, arrival_station, departure_date, train_number, tickets_count)
        time.sleep(10)


async def test_request():
    url = get_rw_url('Минск', 'Витебск', '2023-12-10')
    trains = await get_webpage(url)
    print(trains)
    print(trains['empty_seats_count'])
    print('Количество поездов = ', len(trains['trains']))
    print('found_tickets:', show_brief_info(query_tickets(trains, train_number=None, tickets_count=None)))
    # return show_brief_info(query_tickets(trains, train_number=None, tickets_count=None))
    # print('show_trains', show_trains(trains))


# test_request()
asyncio.run(test_request())
# main_loop('Минск', 'Витебск', '2023-11-26')
