import shutil
import urllib.request
import m3u8


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

for i, segment in enumerate(m3u8_obj.segments):
    print('Загрузка части {} из {}'.format(i, segments_count))
    with urllib.request.urlopen(segment.absolute_uri) as response, open('merged.ts', 'ab') as out_file:
        shutil.copyfileobj(response, out_file)

print('Готово!')
