#!/usr/bin/env python3
from optparse import OptionParser


def parse_arguments():
    parser = OptionParser(usage='usage: %prog [option]... URL...')
    parser.add_option('-i', dest='input_file', metavar='FILE',
                      help='Download URLs found in FILE')
    parser.add_option('-C', dest='cookie_file', default='', metavar='FILE',
                      help='File to load cookies from (WIP)')

    opts, args = parser.parse_args()
    if not args and not opts.input_file:
        parser.print_help()
        exit(1)
    return opts, args
