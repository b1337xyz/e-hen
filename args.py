#!/usr/bin/env python3
from optparse import OptionParser

def parse_arguments():
    parser = OptionParser(usage='usage: %prog [option]... URL...')
    parser.add_option('-d', dest='dir', metavar='PATH',
                      help='Download directory')
    parser.add_option('-i', dest='input_file', metavar='FILE',
                      help='Download URLs found in FILE')
    parser.add_option('-C', dest='cookie_file', default='', metavar='FILE',
                      help='File to load cookies from (WIP)')
    parser.add_option('-A', dest='user_agent', default='', metavar='UA',
                      help='User Agent from when you got your cookies')

    opts, args = parser.parse_args()
    if not args and not opts.input_file:
        parser.print_help()
        exit(1)
    return opts, args




