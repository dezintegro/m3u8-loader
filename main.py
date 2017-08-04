import argparse

from M3U8Loader import M3U8Loader


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Specify m3u8 playlist file. Ignored if -d option selected")
    parser.add_argument("-o", "--output", help="Specify output filename. Ignored if -d option selected")
    parser.add_argument('--async', dest='async', action='store_true')
    args = parser.parse_args()
    print(args)
    loader = M3U8Loader(args.input, args.output, args.async)
    # loader._merge()
    loader.download()
