# -*- coding: utf-8 -*-
import argparse

from src.collector.text.news.sina.finance.SinaFinanceNewsCollector import SinaFinanceNewsCollector


def start_sina_collector(result):
    cat = result.cat
    if cat == "finance":
        collector = SinaFinanceNewsCollector(50)
        collector.collect()


def start_news_collector(result):
    org = result.org
    options = {
        "sina": start_sina_collector,
    }
    options[org](result)


def start_text_collector(result):
    text_type = result.text_type
    options = {
        "news": start_news_collector,
    }
    options[text_type](result)


def start_collector(result):
    type = result.type
    options = {
        "text": start_text_collector,
    }
    options[type](result)


def parse_cmd_result(result):
    cmd = result.cmd
    options = {
        "collect": start_collector,
    }
    options[cmd](result)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-collect', action='store_const', dest='cmd',
                        const='collect',
                        help='Start Collectors')

    parser.add_argument('-analytics', action='store_const', dest='cmd',
                        const='analytics',
                        help='Start Analytics')

    parser.add_argument('-text', action='store_const', dest='type',
                        const='text',
                        help='Collecting text resources')

    parser.add_argument('-news', action='store_const', dest='text_type',
                        const='news',
                        help='Collecting news resources')

    parser.add_argument('--org', action='store', dest='org',
                        help='Provide organization')

    parser.add_argument('--cat', action='store', dest='cat',
                        help='Provide category')

    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    result = parser.parse_args()
    try:
        parse_cmd_result(result)
    except KeyError as e:
        print("Invalid arguments")
    except Exception as e:
        print(str(e))


if __name__ == '__main__':
    main()
