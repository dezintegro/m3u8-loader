import os
import shutil
from time import sleep, time
from multiprocessing import Process

import m3u8

from async_download import *


class M3U8Loader:
    def __init__(self, m3u8_file, out_file=None):
        self.m3u8_file = m3u8_file
        self.max_connections = 50
        self.out = out_file if out_file else '{}.ts'.format(m3u8_file)
        self.tmp_root = 'tmp/'
        self.tmp_folder = '{}{}_tmp/'.format(self.tmp_root, self.out)
        self.m3u8_obj = m3u8.load(m3u8_file)  # this could also be an absolute filename
        self.playlists = self.m3u8_obj.playlists if not self.m3u8_obj.is_endlist else None
        self.resolution_index = -1
        self._segments_count = 0
        self._urls = []
        self.loop = asyncio.get_event_loop()
        self.error_timeout = 100
        self.retrying_count = 3

    def get_resolutions(self):
        if self.playlists:
            return [playlist.stream_info.resolution for playlist in self.playlists]

    def set_resolution(self, resolution_index):
        if self.playlists and resolution_index in self.get_resolutions():
            self.resolution_index = resolution_index

    def _download(self):
        # Prepare workspace
        try:
            os.mkdir(self.tmp_root)
        except OSError as e:
            print(e)
        try:
            os.mkdir(self.tmp_folder)
        except OSError as e:
            # TODO Handle incomplete tasks
            print(e)

        # Prepare data
        if not self.m3u8_obj.is_endlist:
            self.m3u8_obj = m3u8.load(self.playlists[self.resolution_index].absolute_uri)
        self._segments_count = len(self.m3u8_obj.segments)
        segments_urls = [segment.absolute_uri for segment in self.m3u8_obj.segments]
        if self.max_connections > self._segments_count:
            self.max_connections = self._segments_count

        # Async download
        started = time()
        with aiohttp.ClientSession(loop=self.loop) as session:
            loaded = 0
            for part in group(segments_urls, self.max_connections):
                results, errors = self.loop.run_until_complete(
                    fetch_all(session, part, self.tmp_folder))
                loaded += len(results)
                print('Загружено {} частей из {}'.format(loaded, self._segments_count))
                if errors:
                    # TODO Accumulate errors and do n retries
                    for x in range(self.retrying_count):
                        _, errors = self.loop.run_until_complete(fetch_all(session, errors, self.tmp_folder))
                        print('Errors count {}, retrying...'.format(len(errors)))
                        sleep(self.error_timeout)
                        if not errors:
                            break
                    print('Не удалось загрузить {}'.format(len(errors)))
        print('Загрузка завершена за {} сек.'.format(int(time() - started)))


    def _merge(self):
        started = time()
        files = [self.tmp_folder + file.split('/')[-1] for file in os.listdir(self.tmp_folder)]
        total = len(files)
        # TODO TimeIt!
        merged = 0
        with open(self.out, 'ab') as out_file:
            for file in files:
                with open(file, 'rb') as in_file:
                    shutil.copyfileobj(in_file, out_file)
                os.remove(file)
                merged += 1
                print('Обработано {} частей из {}'.format(merged, total))
        print('Обработка завершена за {} сек.'.format(int(time() - started)))

    def download(self):
        self._download()
        self._merge()
        os.removedirs(self.tmp_folder)


if __name__ == '__main__':
    # Process(target=download_video, args=())
    # [download_video('playlists/{}'.format(file), '{}.ts'.format(file)) for file in os.listdir('playlists')[2:]]
    s = M3U8Loader('lection3.m3u8')
    r = s.get_resolutions()
    print(r)
    s.set_resolution(5)
    print(s.resolution_index)
    # s.download()
    s._merge()
    # s = M3U8Loader('master.m3u8')
    # r = s.get_resolutions()
    # print(r)