import asyncio
from datetime import datetime


async def coro(t):
    print('Coro sleep', t)
    await asyncio.sleep(t)


async def main_1():
    """ task2 выполнится только после task1 и общее время составит 3 сек.
        Т.к. не создаются объекты с отложенным выполнением, а task1 и task2 являются просто сопрограммами coro.
    """
    while True:
        task1 = coro(2)
        task2 = coro(1)
        s = datetime.now()
        await task1
        await task2
        print('    Spent time:', datetime.now() - s)


async def main_2():
    """ task2 сразу после начала task1, не дожадаясь его завершения, и общее время составит 2 сек.
        В данной функции сопрограммы coro1 и coro2 преобразуются в таски - будущие объекты с отложенным выполнением.
    """
    while True:
        task1 = asyncio.create_task(coro(2))
        task2 = asyncio.create_task(coro(1))
        s = datetime.now()
        await task1
        await task2
        print('    Spent time:', datetime.now() - s)


asyncio.run(main_1())
# asyncio.run(main_2())


async def main_sequent():
    """ Список tasks содержит обычные сопрограммы и общее время выполнеия составит 20 сек.
    """
    while True:
        tasks = []
        for _ in range(10):
            tasks.append(coro(2))
        s = datetime.now()
        for task in tasks:
            await task
        print('    Spent time:', datetime.now() - s)


async def main_concur():
    """ Список tasks содержит будущие объкты task и общее время выполнеия составит 2 сек.
    """
    while True:
        tasks = []
        for _ in range(10):
            tasks.append(asyncio.create_task(coro(2)))
        s = datetime.now()
        for task in tasks:
            await task
        print('    Spent time:', datetime.now() - s)


# asyncio.run(main_sequent())
# asyncio.run(main_concur())
