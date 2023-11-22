import asyncio


async def start():
    print('hello')
    await asyncio.sleep(1)
    print('world')

asyncio.run(start())


def simple_coroutine():
    c = 0
    print('-> coroutine started, c =', c)
    while True:
        print('-> coroutine continue, c = ', c)
        x = yield
        print('-> coroutine received:', x)
        c += 1


def main():
    print("Main started")
    coro = simple_coroutine()
    next(coro)
    while True:
        p = input('Enter char. "q" - EXIT: ')
        if p == 'q':
            break
        coro.send(p)


# main()

