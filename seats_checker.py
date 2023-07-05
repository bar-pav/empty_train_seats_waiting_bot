from datetime import datetime
import time

import requests
from bs4 import BeautifulSoup as bs


with open('my_telegram_token.txt', 'r') as file:
    telegram_token = file.read()

with open('my_telegram_id.txt', 'r') as file:
    my_telegram_id = file.read()

route = ('Витебск', 'Минск-Пассажирский')

# --------------------------------------------------------------
# departure_date = None
departure_date = {
    'day': '01',
    'month': '01',
    'year': '2024'
}


if isinstance(departure_date, dict):
    date = f"{departure_date['year']}-{departure_date['month']}-{departure_date['day']}"
else:
    date = input("Enter departure date in format 'YYYY-MM-DD' (YEAR-MONTH-DAY):\n")

print(f"Enter departure station (1 - Vitebsk) (2 - Minsk):")
dep = input("\tStation: ")
if dep == '1' or dep == 'Vitebsk':
    route_from, route_to = route
else:
    route_from, route_to = route[::-1]

telegram_url = "https://api.telegram.org/bot" + telegram_token + '/sendMessage' + '?chat_id=' + my_telegram_id + '&text='
rw_url = f"https://pass.rw.by/ru/route/?from={route_from}&to={route_to}&date={date}"


def send_msg(text):
    url = telegram_url + text
    result = requests.get(url)
    print(result.json())


def get_list_of_trains():
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
        print('Exception while getting list of trains.')


def print_list_of_trains(trains):
    print('Select train:')
    if trains:
        for i, train in enumerate(trains, start=1):
            print(f"\t{i}) '{train[0]}' : {train[1]} - {train[2]}")


def get_seats_info(data_train_number):
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


def main_loop():
    trains = get_list_of_trains()
    print_list_of_trains(trains)
    if trains:
        number = int(input(f"Select train number. Enter 1 - {len(trains)}:  "))
        train_number = trains[number - 1][0]
    else:
        print('No trains on selected date.')
        return
    while True:
        print(datetime.now().strftime('%d.%m %H:%M:%S'), end=' ')
        print(f"'{trains[number - 1][3]}'", end=" ")
        print(f"Train '{train_number}': {departure_date['day']}/{departure_date['month']}/{departure_date['year']},", end=' ')
        get_seats_info(train_number)
        time.sleep(10)


main_loop()
