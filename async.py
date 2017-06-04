import shutil
import m3u8
from async_download import *


MAX_CONNECTIONS = 100
resolution_index = 1
infile = 'merged.ts'
outfile = 'merged.mp4'

m3u8_obj = m3u8.load('master.m3u8')  # this could also be an absolute filename
playlists = m3u8_obj.playlists

print('Доступные разрешения:')
for playlist in playlists:
    print(playlist.stream_info.resolution)

# TODO выбор разрешения

m3u8_obj = m3u8.load(playlists[resolution_index].absolute_uri)
segments_count = len(m3u8_obj.segments)
print('Всего {} частей'.format(segments_count))
urls = [segment.absolute_uri for segment in m3u8_obj.segments]  # [:10]
files = ['tmp/' + file.split('/')[-1] for file in urls]

loop = asyncio.get_event_loop()

with aiohttp.ClientSession(loop=loop) as session:
    for part in group(urls, MAX_CONNECTIONS):
        results, errors = loop.run_until_complete(
            fetch_all(session, part, loop))
        if errors:
            _, errors = loop.run_until_complete(fetch_all(session, errors, loop))
            print('Не удалось загрузить {}'.format(len(errors)))

print('Загрузка завершена')
print('Обработка файлов')
for file in files:
    with open(file, 'rb') as in_file, open('merged.ts', 'ab') as out_file:
        shutil.copyfileobj(in_file, out_file)

#
# for i, segment in enumerate(m3u8_obj.segments):
#     print('Загрузка части {} из {}'.format(i, segments_count))
#     with urllib.request.urlopen(segment.absolute_uri) as response, open('merged.ts', 'ab') as out_file:
#         shutil.copyfileobj(response, out_file)

# print('Конвертируем видео')

# subprocess.run(['ffmpeg', '-i', infile, outfile])
print('Готово!')
