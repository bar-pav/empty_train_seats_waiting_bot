import asyncio
import datetime


async def coro(start_time):
    print('        Start coro.')
    await asyncio.sleep(1)
    print('            coro sleep on 1 sec.')
    print('        Stop coro.')
    print('    coro time: ', datetime.datetime.now() - start_time)


async def supervisor():
    s = datetime.datetime.now()
    cr = asyncio.create_task(coro(s))
    print('TASK CREATED.')
    print('    main thread sleep on 4 sec.')
    await asyncio.sleep(4)
    print('TASKS ENDED')
    cr.cancel()
    end_sv = datetime.datetime.now()
    print('Time: ')
    print('    supervisor: ', end_sv - s)


def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(supervisor())
    loop.close()


main()
