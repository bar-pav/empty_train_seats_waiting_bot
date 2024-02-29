import calendar

import datetime

import logging


# print([datetime.date(2001, 1, i+1).strftime('%A') for i in range(7)])
# print([datetime.date(2001, 1, i+1).strftime('%a') for i in range(7)])
# print([datetime.date(2001, 1, i+1).strftime('%B') for i in range(7)])

logging.basicConfig(level=logging.DEBUG)

cal = calendar.Calendar(0)
start = datetime.datetime.now()

print(cal.yeardayscalendar(2023, 1))
print('weekdays: ', list(cal.iterweekdays()))
print('itermonthdays: ', list(cal.itermonthdays(2024, 2)))
print('itermonthdates: ', list(cal.itermonthdates(2024, 2)))
print('itermonthdays3: ', list(cal.itermonthdays3(2024, 2)))
print('monthdatescalendar: ', list(cal.monthdatescalendar(2024, 2)))
print('itermonthdays4: ', list(cal.itermonthdays4(2024, 2)))
print('monthdayscalendar: ', list(cal.monthdayscalendar(2024, 2)))

print()


def print_month_calendar(year, month):
    for week in cal.monthdayscalendar(year, month):
        for day in week:
            print(f'{day:2}', end=' ', )
        print()


def one_month_offset(year, month, offset):
    if offset not in (-1, +1):
        return year, month
    month = month + offset
    if month < 1:
        month = 12
        year = year - 1
    if month > 12:
        month = 1
        year = year + 1
    return year, month


def next_month(year, month):
    return one_month_offset(year, month, 1)


def prev_month(year, month):
    return one_month_offset(year, month, -1)


print_month_calendar(*one_month_offset(2024, 1, -1))
print_month_calendar(2024,1)
print_month_calendar(2024,2)
print_month_calendar(2024,3)
print_month_calendar(2024,4)

# print(one_month_offset(2024, 0, -1))


# for day in cal.monthdatescalendar(2023, 2):
#     print(day)
# print((datetime.datetime.now() - start))

# for quarter in cal.yeardayscalendar(2024):
#     print(quarter)
#     for mon in quarter:
#         # print('month: ', mon)
#         for weeks in mon:
#             print(weeks)
#     print()

