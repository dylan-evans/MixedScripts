#!/usr/bin/env python
"""
Quick script for sorting files into subdirectories by modification time. It
is intended for the occasion where the user stumbles across a directory with
hundreds of thousands of files in it
"""
from __future__ import print_function

import os
import sys
import stat
import shutil
import argparse
from datetime import datetime


def _parse_args(argv):
    """
    Parse the command line.
    :param argv: A list of arguments.
    """
    parser = argparse.ArgumentParser(
        description="Sort files into date based subdirectories"
    )
    parser.add_argument("--granularity", "-g", default="daily",
                        choices=("daily", "monthly", "yearly"),
                        help="Sort files daily, monthly or yearly")
    parser.add_argument("--ignore-dirs", "-i", action="store_true",
                        help="Don't sort directories")
    parser.add_argument("--source", "-s", default=".",
                        help="The directory to move/copy from")
    parser.add_argument("--destination", "-d", default=".",
                        help="The directory to put the files into")
    parser.add_argument("--copy", "-c", action="store_true",
                        help="Copy files instead of moving them")

    return parser.parse_args(argv)


def _main(args):
    """
    Main code for the sort.
    :param args: An object which represents the command line parameters.
    """
    for filename in os.listdir(args.source):
        filepath = os.path.join(args.source, filename)

        # At the risk of obfuscation this will do a single stat
        info = os.stat(filepath)
        mtime = datetime.fromtimestamp(info.st_mtime)
        sub = mtime.strftime(get_date_format(args.granularity))
        dest = os.path.join(args.destination, sub)

        isdir = stat.S_ISDIR(info.st_mode)

        if not isdir or not args.ignore_dirs:
            shift_file(filepath, dest, isdir=isdir, iscopy=args.copy)


def shift_file(source, dest, isdir=False, iscopy=False):
    """
    Move or copy files depending on the value of iscopy. Selects the
    best function for the particular job.
    :param source: The source file or directory.
    :param dest: The destination directory.
    :param isdir: Must be set to true if the source is a directory.
    :param iscopy: Set to true to copy files instead of moving them.
    """
    # This is going to cost an extra stat for each file
    if not os.path.exists(dest):
        os.makedirs(dest)
    if iscopy:
        print("Copying", os.path.basename(source), "to", dest)
        if isdir:
            dest = os.path.join(dest, os.path.basename(source))
            shutil.copytree(source, dest, symlinks=True)
        else:
            shutil.copy2(source, dest)
    else:
        print("Moving", os.path.basename(source), "to", dest)
        shutil.move(source, dest)


def get_date_format(granularity):
    """
    Return a strftime string for the specified granularity. This function does
    not attempt to check for errors and returns daily by default.
    :param granularity: The granularity of date based directories.
    """
    if granularity == "yearly":
        return os.sep.join(("%Y", ""))
    if granularity == "monthly":
        return os.sep.join(("%Y", "%m", ""))
    return os.sep.join(("%Y", "%m", "%d", ""))


if __name__ == "__main__":
    _main(_parse_args(sys.argv[1:]))
