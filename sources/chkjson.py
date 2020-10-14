#!/usr/bin/env python3
# scanjson.py -- Scan JSON from Legiscan API
# By Tony Pearson, IBM, 2020
#
import base64
import codecs
import json
import re
import sys

charForm = "{} for {} on {} from position {} to {}. Using '?' in-place of it!"


class Stats():
    """
    Class to identify minimum, maximum and average lenght of strings

    """

    def __init__(self, id, limit):
        """ Set characters to use for showing progress"""
        self.id = id
        self.limit = limit
        self.min = None
        self.max = None
        self.total = 0
        self.count = 0
        self.overlim = 0
        self.ShowForm = "{} Min: {}  Average: {}   Maximum {}  Count {}  Over {}"
        return None

    def add_stat(self, num):
        if self.count == 0:
            self.min = num
            self.max = num
        elif num < self.min:
            self.min = num
        elif num > self.max:
            self.max = num
        if num > self.limit:
            self.overlim += 1

        self.total += num
        self.count += 1
        return self

    def show_stat(self):
        result = self.id + " No statistics"
        if self.count > 0:
            avg = self.total // self.count
            result = self.ShowForm.format(self.id, self.min, avg, 
                                          self.max, self.count, self.overlim)
        return result

def remove_section_numbers(line):
    newline = re.sub(r'and [0-9]+[.][0-9]+\b\s*', '', line)
    newline = re.sub(r'\([0-9]+[.][0-9]+\)[,]?\s*', '', newline)  
    newline = re.sub(r'\b[0-9]+[.][0-9]+\b[,]?\s*', '', newline)
    newline = re.sub(r'section[s]? and section[s]?\s*', 'sections', newline)
    newline = re.sub(r'section[s]?\s*;\s*', '; ', newline)
    newline = re.sub(r'amend; to amend,\s*', 'amend ', newline)
    newline = newline.replace("'", " ").replace('"', ' ')
    return newline


def shrink_line(line, limit):
    newline = re.sub(r'^\W*\w*\W*', '', line[-limit:])
    newline = re.sub(r'^and ', '', newline)
    newline = newline[0].upper() + newline[1:]
    return newline


def get_parms(argv):
    display_help = False
    filename = ''
    if len(sys.argv) == 2:
        filename = sys.argv[1]
        if filename == '--help' or filename == '-h':
            display_help = True
        if not filename.endswith('.json'):
            display_help = True
    else:
        display_help = True

    if display_help:
        print('Syntax:')
        print(sys.argv[0], 'input_file.json')
        print(' ')

    return display_help, filename


def custom_character_handler(exception):
    print(charForm.format(exception.reason,
            exception.object[exception.start:exception.end],
            exception.encoding,
            exception.start,
            exception.end ))
    return ("?", exception.end)


if __name__ == "__main__":
    # Check proper input syntax
    codecs.register_error("custom_character_handler", custom_character_handler)

    display_help, jsonname = get_parms(sys.argv)
    state = jsonname[:2].upper()

    keystats = Stats('Key', 20)
    titlestats = Stats('Title', 200)
    summarystats = Stats('Summary', 1000)
    billstats = Stats('Billtext', 4000000)

    if not display_help:
        with open(jsonname, "r") as jsonfile:
            data = json.load(jsonfile)
            for entry in data:
                bill = data[entry]
                key = "{}-{}.txt".format(state, bill['number'])
                title = remove_section_numbers(bill['title'])
                summary = remove_section_numbers(bill['description'])
                # print('KEY: ', key)
                # print('TITLE: ', title)
                # print('SUMMARY: ', summary)

                if len(title)>200:
                    revised = shrink_line(title, 200)

                if len(summary)>1000:
                    revised = shrink_line(summary, 1000)
                
                keystats.add_stat(len(key))
                titlestats.add_stat(len(title))
                summarystats.add_stat(len(summary))
                billstats.add_stat(len(bill['bill_text']))

    print(' ')
    print('Statistics:')
    print(keystats.show_stat())
    print(titlestats.show_stat())
    print(summarystats.show_stat())
    print(billstats.show_stat())
    print('Done.')