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
departure_station = get_departure_station()
arrival_station = get_arrival_station()
# --------------------------------------------------------------


def get_departure_date():
    return input("Введите дату отправления в формате dd.mm.yyyy.").strip()


departure_date = get_departure_date().split('.')
departure_date = {
    'day': departure_date[0],
    'month': departure_date[1],
    'year': departure_date[2]
}
    
if isinstance(departure_date, dict):
    departure_date = f"{departure_date['year']}-{departure_date['month']}-{departure_date['day']}"
else:
    departure_date = input("Enter departure date in format 'YYYY-MM-DD' (YEAR-MONTH-DAY):\n")


print(f"Enter departure station (1 - Vitebsk) (2 - Minsk):")
dep = input("\tStation: ")
if dep == '1' or dep == 'Vitebsk':
    route_from, route_to = route
else:
    route_from, route_to = route[::-1]

telegram_url = "https://api.telegram.org/bot" + telegram_token + '/sendMessage' + '?chat_id=' + my_telegram_id + '&text='


def get_rw_url(from_, to_, date):
    return f"https://pass.rw.by/ru/route/?from={from_}&to={to_}&date={date}"


def send_msg(text):
    url = telegram_url + text
    result = requests.get(url)
    print(result.json())


def get_list_of_trains(rw_url):
    try:
        response = requests.get(rw_url)
        page = bs(response.text, features="html.parser")
        if response.status_code == 200:
            trains_list = []
            trains_block = page.find('div', attrs={'class': 'sch-table__body js-sort-body'})
            for i in trains_block.findChildren('div', recursive=False):
                train = []
                if 'data-train-info' in i.attrs:
                    train.append(i.findChild('div')['data-train-number'])
                    train.append(i.find('div', attrs={'data-sort': 'departure'}).text.strip())
                    train.append(i.find('div', attrs={'data-sort': 'arrival'}).text.strip())
                    train.append(i.find('span', attrs={'class': 'train-route'}).text.strip())
                    trains_list.append(train)
            return trains_list
    except:
        print(f"Exception while getting list of trains on date {departure_date} for route '{route_from} - {route_to}'.")
        return

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
                if found.find('div', attrs={'class': 'sch-table__no-info'}) or found.find('div', attrs={'class': 'sch-table__cell cell-4 empty'}):
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


main_loop(departure_station, arrival_station, departure_date)
