import os
import shutil
from time import sleep

import m3u8

from async_download import *


def download_video(m3u8_file, outfile):
    print(m3u8_file)
    MAX_CONNECTIONS = 100
    resolution_index = -1
    tmp_root = 'tmp/'
    tmp_folder = '{}{}_tmp/'.format(tmp_root, outfile)

    # TODO handle uncompleted loads here
    try:
        os.mkdir(tmp_root)
        os.mkdir(tmp_folder)
    except OSError as e:
        print(e)
    m3u8_obj = m3u8.load(m3u8_file)  # this could also be an absolute filename
    if not m3u8_obj.is_endlist:
        playlists = m3u8_obj.playlists

        print('Доступные разрешения:')
        for playlist in playlists:
            print(playlist.stream_info.resolution)

        # TODO выбор разрешения
        m3u8_obj = m3u8.load(playlists[resolution_index].absolute_uri)


    segments_count = len(m3u8_obj.segments)
    print('Всего {} частей'.format(segments_count))
    urls = [segment.absolute_uri for segment in m3u8_obj.segments]  # [:10]
    files = [tmp_folder + file.split('/')[-1] for file in urls]
    count = len(urls)
    loop = asyncio.get_event_loop()

    with aiohttp.ClientSession(loop=loop) as session:
        loaded = 0
        for part in group(urls, MAX_CONNECTIONS):
            results, errors = loop.run_until_complete(
                fetch_all(session, part, tmp_folder))
            loaded += len(part)
            print('Загружено {} частей из {}'.format(loaded, count))
            if errors:
                # TODO Accumulate errors and do n retries
                for x in range(5):
                    _, errors = loop.run_until_complete(fetch_all(session, errors, tmp_folder))
                    print('Errors count {}, retrying...'.format(len(errors)))
                    sleep(100)
                    if not errors:
                        break
                print('Не удалось загрузить {}'.format(len(errors)))


    print('Загрузка завершена')
    print('Обработка файлов')
    for file in files:
        with open(file, 'rb') as in_file, open(outfile, 'ab') as out_file:
            shutil.copyfileobj(in_file, out_file)
        os.remove(file)
    # os.removedirs(tmp_folder)
    print('Готово!')


if __name__ == '__main__':
    [download_video('playlists/{}'.format(file), '{}.ts'.format(file)) for file in os.listdir('playlists')]