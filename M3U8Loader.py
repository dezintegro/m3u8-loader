import os
import shutil
import urllib.request
from time import sleep, time

import m3u8

from async_download import *


class M3U8Loader:
    def __init__(self, m3u8_file, out_file=None, async=False):
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
        self.error_timeout = 5
        self.retrying_count = 3
        self.async = async

    def get_resolutions(self):
        if self.playlists:
            return [playlist.stream_info.resolution for playlist in self.playlists]

    def set_resolution(self, resolution_index):
        if self.playlists and resolution_index in self.get_resolutions():
            self.resolution_index = resolution_index

    def _resolve_playlist(self):
        if not self.m3u8_obj.is_endlist:
            self.m3u8_obj = m3u8.load(self.playlists[self.resolution_index].absolute_uri)
        self._segments_count = len(self.m3u8_obj.segments)

    def _download_sync(self):
        self._resolve_playlist()

        # Synchronous downloading parts directly into out file
        started = time()
        with open(self.out, 'ab') as out_file:
            for i, segment in enumerate(self.m3u8_obj.segments):
                print('Загрузка части {} из {}'.format(i, self._segments_count))
                with urllib.request.urlopen(segment.absolute_uri) as response:
                    shutil.copyfileobj(response, out_file)
        print('Загрузка завершена за {} сек.'.format(int(time() - started)))

    def _download_async(self):
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
        self._resolve_playlist()
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
                # print_progress_bar(loaded, self._segments_count, prefix='Downloading:', suffix='Complete', length=50)
                print('Загружено {} частей из {}'.format(loaded, self._segments_count))
                if errors:
                    # TODO Accumulate errors and do n retries
                    for x in range(self.retrying_count):
                        print('Errors count {}, retrying...'.format(len(errors)))
                        _, errors = self.loop.run_until_complete(fetch_all(session, errors, self.tmp_folder))
                        sleep(self.error_timeout)
                        if not errors:
                            break
                    else:
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
                if not merged % 100 or merged == total:
                    print('Обработано {} частей из {}'.format(merged, total))
                    # print_progress_bar(merged, total, prefix='Processing:', suffix='Complete', length=50)

        print('Обработка завершена за {} сек.'.format(int(time() - started)))

    def download(self):
        if self.async:
            self._download_async()
            self._merge()
            os.removedirs(self.tmp_folder)
        else:
            self._download_sync()

if __name__ == '__main__':
    pass
