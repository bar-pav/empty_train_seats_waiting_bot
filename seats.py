from datetime import datetime
import time
from bs4 import BeautifulSoup as bs
import requests

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


def get_list_of_trains(rw_url):
    pass


def print_list_of_trains(trains):
    print('Select train:')
    if trains:
        for i, train in enumerate(trains, start=1):
            print(f"\t{i}) '{train[0]}' : {train[1]} - {train[2]}")


def get_seats_info(data_train_number, rw_url):
    try:
        response = requests.get(rw_url)
        page = bs(response.text, features="html.parser")
    except:
        print('No responses. Check Internet connection.')
        time.sleep(10)
        return
    # print(response.status_code)
    if response.status_code == 200:
        try:
            found = page.find('div', attrs={'class': 'sch-table__row', 'data-train-number': data_train_number})
            if found:
                dep_time = found.find('div', attrs={'class': 'sch-table__time train-from-time'}).text
                print(f"{dep_time}", end=':   ')
                if found.find('div', attrs={'class': 'sch-table__no-info'}) or found.find('div', attrs={
                    'class': 'sch-table__cell cell-4 empty'}):
                    print('No seats')
                else:
                    send_msg("There are seats")
            else:
                # print("There is no div with attributes {'class': 'sch-table__row', 'data-train-number': data_train_number}")
                print('Data is not exist with some attributes.')
        except Exception:
            print('Something went wrong.')
    else:
        print('Status code is not 200')


def test_get_updates_from_bot():
    url = "https://api.telegram.org/bot" + telegram_token + '/getUpdates'
    result = requests.get(url)
    print(result.json())


def get_rw_url(from_, to_, date):
    return f"https://pass.rw.by/ru/route/?from={from_}&to={to_}&date={date}"


def parse_response(response):
    empty_seats_count = 0
    trains = {}
    page = bs(response.text, features="html.parser")
    train_blocks = page.css.select('div[data-train-info]')
    # train_table = page.find('div', attrs={'class': 'sch-table__body js-sort-body'})
    # print(train_table)
    # train_blocks = train_table.find_all('div', recursive=False)
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

        no_tickets = train_block.find('div', attrs={'class': 'sch-table__no-info'})
        if no_tickets:
            tickets = no_tickets.text.strip()

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


def get_trains(rw_url):
    s = datetime.now()
    response = requests.get(rw_url)
    er = datetime.now()
    if response.status_code == 200:
        trains = parse_response(response)
        ep = datetime.now()
        print("Response spent time:", er - s, 's')
        print("Parse spent time:", ep - er, 's')

        return trains
        # trains_list = []
        # train_blocks = page.find('div', attrs={'class': 'sch-table__body js-sort-body'})
        # for i in train_blocks.findChildren('div', recursive=False):
        #     train = []
        #     if 'data-train-info' in i.attrs:
        #         train.append(i.findChild('div')['data-train-number'])
        #         train.append(i.find('div', attrs={'data-sort': 'departure'}).text.strip())
        #         train.append(i.find('div', attrs={'data-sort': 'arrival'}).text.strip())
        #         train.append(i.find('span', attrs={'class': 'train-route'}).text.strip())
        #         trains_list.append(train)
        # return trains_list


def main_loop(departure_station, arrival_station, departure_date):
    trains = None
    while trains is None:
        rw_url = get_rw_url(departure_station, arrival_station, departure_date)
        trains = get_list_of_trains(rw_url)
        if trains is None:
            departure_date = input("Enter another departure date in format 'YYYY-MM-DD' (YEAR-MONTH-DAY):\n")
    print_list_of_trains(trains)
    if trains:
        number = int(input(f"Select train number. Enter 1 - {len(trains)}:  "))
        train_number = trains[number - 1][0]
    else:
        print('No trains on selected date.')
        return
    while True:
        print(datetime.now().strftime('%d.%m %H:%M:%S'), end=': ')
        print(f"'{trains[number - 1][3]}'", end=" ")
        print(f"Train '{train_number}': {departure_date},", end=' ')
        get_seats_info(train_number, rw_url)
        time.sleep(10)


# main_loop(departure_station, arrival_station, departure_date)


def test_request():
    url = get_rw_url('Минск', 'Витебск', '2023-11-24')
    trains = get_trains(url)
    print(trains)
    print(trains['empty_seats_count'])
    print('Количество поездов = ', len(trains['trains']))


test_request()
