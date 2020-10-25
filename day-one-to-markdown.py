#!/usr/bin/env python3

import argparse
import json
import os
import re
import shutil
import tempfile
import zipfile

import dateutil.parser
import frontmatter


class Zip(object):

    def __init__(self, path):
        self.path = os.path.abspath(path)

    def __enter__(self):
        self.directory = tempfile.TemporaryDirectory()
        zip = zipfile.ZipFile(self.path, 'r')
        zip.extractall(self.directory.name)
        return self

    def __exit__(self, *args, **kwargs):
        self.directory.cleanup()
        pass


class Photo(object):

    def __init__(self, directory, data):
        self.directory = directory
        self.data = data

    @property
    def basename(self):
        return "%s%s" % (self.data["md5"], self.ext)

    @property
    def path(self):
        return os.path.join(self.directory, self.basename)


    @property
    def ext(self):
        try:
            return ".%s" % (self.data["type"], )
        except KeyError:
            return ".jpeg"


class Markdown(object):

    def __init__(self, content=None, metadata=None):
        self.content = content
        self.metadata = metadata


def main():
    parser = argparse.ArgumentParser(description="Convert a Day One JSON export to Markdown.")
    parser.add_argument("path")
    parser.add_argument("destination")
    options = parser.parse_args()

    destination = os.path.abspath(options.destination)

    with Zip(options.path) as zip:
        with open(os.path.join(zip.directory.name, "Journal.json"), "r") as fh:
            data = json.load(fh)
            directory = os.path.join(os.path.dirname(options.path))

        for post in data["entries"]:

            date = dateutil.parser.parse(post["creationDate"])
            post_directory = os.path.join(destination, "%s-%s" % (date.strftime("%Y-%m-%d"), post["uuid"].lower()))

            os.makedirs(post_directory)

            photos = {data["identifier"]: Photo(os.path.join(zip.directory.name, "photos"), data) for data in post["photos"]}
            for identifier, photo in photos.items():
                shutil.copy(photo.path, os.path.join(post_directory, photo.basename))

            content = post["text"]

            def replacement(match):
                return photos[match.group(1)].basename

            content = re.sub("dayone-moment://([0-9a-zA-Z]+)", replacement, content)

            metadata = dict(post)
            del metadata["text"]
            del metadata["photos"]
            metadata["date"] = metadata["creationDate"]
            del metadata["creationDate"]
            try:
                metadata["location"]["title"] = metadata["location"]["placeName"]
            except KeyError:
                pass
            markdown = Markdown(content=content, metadata=metadata)

            with open(os.path.join(post_directory, "index.markdown"), "w") as fh:
                fh.write(frontmatter.dumps(markdown))
                fh.write("\n")


if __name__ == "__main__":
    main()
