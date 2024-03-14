import asyncio
from datetime import datetime, timedelta
from async_seats import get_rw_url, get_webpage, parse_response, filter_tickets, trains_brief_info


async def test_request():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    url = get_rw_url('Минск', 'Витебск', tomorrow)
    page = await get_webpage(url)
    if page:
        trains, seats_count = parse_response(page)
        print(trains)
        print('Количество поездов = ', len(trains))
        print('Найденные билеты:')
        t = list(filter_tickets(trains, train_number=None, tickets_count=None))
        print(t)
        print(trains_brief_info(t))
    else:
        print('No page. Check request parameters.')


if __name__ == "__main__":
    asyncio.run(test_request())
