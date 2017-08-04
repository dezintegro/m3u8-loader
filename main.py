import argparse

from async import M3U8Loader


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="Specify m3u8 playlist file. Ignored if -d option selected")
    parser.add_argument("-o", "--output", default='123', help="Specify output filename. Ignored if -d option selected")
    args = parser.parse_args()
    loader = M3U8Loader(args.input, args.output)
    loader.download()
    print(args)
