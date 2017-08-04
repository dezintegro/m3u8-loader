import aiohttp
import asyncio
from itertools import zip_longest


# Print iterations progress
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled = int(length * iteration // total)
    bar = fill * filled + '-' * (length - filled)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if iteration == total:
        print()


def group(iterable, count):
    """ Группировка элементов последовательности по count элементов """

    return zip_longest(*[iter(iterable)] * count)


async def fetch(session, url, tmp_folder):
    if not url:
        return
    filename = tmp_folder + url.split('/')[-1]
    async with session.get(url) as response:
        with open(filename, 'wb') as f_handle:
            while True:
                # data = await response.read()
                data = await response.content.read(512)
                if not data:
                    break
                f_handle.write(data)
        # print('Загрузка части {} завершена'.format(filename))
        return await response.release()


async def fetch_all(session, urls, tmp_folder):
    errors = []
    results = await asyncio.gather(
        *[fetch(session, url, tmp_folder) for url in urls],
        return_exceptions=True  # default is false, that would raise
    )

    # for testing purposes only
    # gather returns results in the order of coros
    for idx, url in enumerate(urls):
        if isinstance(results[idx], Exception):
            e = results[idx]
            errors.append(url)
    # print('Ошибок: {}'.format(len(errors)))

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