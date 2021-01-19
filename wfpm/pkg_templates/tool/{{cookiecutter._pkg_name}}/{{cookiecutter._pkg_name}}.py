#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess


def main():
    """
    Python implementation of tool: {{ cookiecutter._pkg_name }}

    This is auto-generated Python code, please update as needed!
    """

    parser = argparse.ArgumentParser(description='Tool: {{ cookiecutter._pkg_name }}')
    parser.add_argument('-i', '--input-file', dest='input_file', type=str,
                        help='Input file', required=True)
    parser.add_argument('-o', '--output-dir', dest='output_dir', type=str,
                        help='Output directory', required=True)
    args = parser.parse_args()

    if not os.path.isfile(args.input_file):
        sys.exit('Error: specified input file %s does not exist or is not accessible!' % args.input_file)

    if not os.path.isdir(args.output_dir):
        sys.exit('Error: specified output dir %s does not exist or is not accessible!' % args.output_dir)

    subprocess.run(f"fastqc -o {args.output_dir} {args.input_file}", shell=True, check=True)


if __name__ == "__main__":
    main()
