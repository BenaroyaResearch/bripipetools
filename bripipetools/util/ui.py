import os
import sys
import __builtin__

def prompt_raw(prompt_text):
    """
    Display prompt text and ask for raw input.
    """
    sys.stderr.write('{}\n'.format(prompt_text))
    return __builtin__.raw_input()

def list_options(option_list):
    """
    Display formatted list of objects in numbered order.
    """
    for idx, option in enumerate(option_list):
        print("%3d : %s" % (idx, option))

def input_to_int(input_func):
    """
    Collect input from function and convert to integer.
    """
    input_raw = input_func()
    if len(input_raw):
        print('\nHERE IS INPUT: >{}<'.format(input_raw))
        print('LENGTH OF INPUT?')
        print('{}\n'.format(len(input_raw)))
        return int(input_func())

def parse_input_list(input_str, sep=','):
    """
    Split input string based on separator and return list.
    """
    return input_str.split(sep)
