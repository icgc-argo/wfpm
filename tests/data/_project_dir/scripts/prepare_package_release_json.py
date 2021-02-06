#!/usr/bin/env python3

# this is a temporary solution

import argparse
import json


def update_image_digest(package_meta, release_meta_str):
    with open(package_meta, 'r') as f:
        package_meta = json.load(f)

    release_meta = json.loads(release_meta_str)

    if 'container' in package_meta:
        package_meta['container']['_image_digest'] = release_meta['_image_digest']
    package_meta['_release'] = release_meta['_release']

    return package_meta


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update pkg.json to generate pkg-release.json ')
    parser.add_argument('-p', dest='package_meta', type=str, required=True)
    parser.add_argument('-d', dest='release_meta_str', type=str, required=True)
    args = parser.parse_args()

    updated_meta = update_image_digest(
        args.package_meta,
        args.release_meta_str
    )

    print(json.dumps(updated_meta, indent=4, sort_keys=True))
