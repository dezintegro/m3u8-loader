import aiohttp
import asyncio
from itertools import zip_longest


def group(iterable, count):
    """ Группировка элементов последовательности по count элементов """

    return zip_longest(*[iter(iterable)] * count)


async def fetch(session, url):
    filename = 'tmp/' + url.split('/')[-1]
    async with session.get(url) as response:
        with open(filename, 'wb') as f_handle:
            while True:
                # data = await response.read()
                data = await response.content.read(512)
                if not data:
                    break
                f_handle.write(data)
        print('Загрузка части {} завершена'.format(filename))
        return await response.release()


async def fetch_all(session, urls, loop):
    errors = []
    results = await asyncio.gather(
        *[fetch(session, url) for url in urls],
        return_exceptions=True  # default is false, that would raise
    )

    # for testing purposes only
    # gather returns results in the order of coros
    for idx, url in enumerate(urls):
        if isinstance(results[idx], Exception):
            e = results[idx]
            errors.append(url)
    print('Ошибок: {}'.format(len(errors)))

    return results, errors

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    # breaks because of the first url
    urls = [
        'http://SDFKHSKHGKLHSKLJHGSDFKSJH.com',
        'http://google.com',
        'http://twitter.com']
    with aiohttp.ClientSession(loop=loop) as session:
        the_results = loop.run_until_complete(
            fetch_all(session, urls, loop))