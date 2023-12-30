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
        zip = zipfile.ZipFile(self.path, "r")
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
            return ".%s" % (self.data["type"],)
        except KeyError:
            return ".jpeg"


class Markdown(object):
    def __init__(self, content=None, metadata=None):
        self.content = content
        self.metadata = metadata


def main():
    parser = argparse.ArgumentParser(
        description="Convert a Day One JSON export to Markdown."
    )
    parser.add_argument("path")
    parser.add_argument("destination")
    parser.add_argument(
        "--journal",
        dest="journal",
        help="day one journal collection to export",
        required=False,
        action="store",
    )
    options = parser.parse_args()

    if options.journal != "":
        journal_js = options.journal + ".json"
        destination = os.path.abspath(options.destination + "/" + options.journal)
    else:
        # use the default journal name
        journal_js = "Journal.json"
        destination = os.path.abspath(options.destination)

    with Zip(options.path) as zip:
        with open(os.path.join(zip.directory.name, journal_js), "r") as fh:
            data = json.load(fh)
            directory = os.path.join(os.path.dirname(options.path))

        for post in data["entries"]:
            date = dateutil.parser.parse(post["creationDate"])
            post_directory = os.path.join(
                destination, "%s-%s" % (date.strftime("%Y-%m-%d"), post["uuid"].lower())
            )

            os.makedirs(post_directory)

            photos = []
            if "photos" in post:
                photos = {
                    data["identifier"]: Photo(
                        os.path.join(zip.directory.name, "photos"), data
                    )
                    for data in post["photos"]
                }

                for _, photo in photos.items():
                    if "md5" not in photo.data:
                        print(f'[ERROR] photo without md5, etc. ({post["uuid"]})')
                        photo.data["md5"] = "stubbed_basename"
                        continue

                    try:
                        shutil.copy(
                            photo.path, os.path.join(post_directory, photo.basename)
                        )
                    except FileNotFoundError:
                        print(
                            f"""[ERROR]photo copy failed: ({post["uuid"]})
  src: {photo.path}
  dst: {os.path.join(post_directory, photo.basename)}"""
                        )

            try:
                content = post["text"]
            except KeyError:
                print(f'[ERROR] post without text ({post["uuid"]})')
                content = ""

            def replacement(match):
                return photos[match.group(1)].basename

            content = re.sub("dayone-moment://([0-9a-zA-Z]+)", replacement, content)

            metadata = dict(post)

            # remove extraneous fields from metadata
            for d in ["text", "richText", "photos"]:
                if d in metadata:
                    del metadata[d]

            metadata["date"] = metadata["creationDate"]
            del metadata["creationDate"]
            try:
                metadata["location"]["title"] = metadata["location"]["placeName"]
            except KeyError:
                pass
            markdown = Markdown(content=content, metadata=metadata)

            with open(os.path.join(post_directory, "index.md"), "w") as fh:
                fh.write(frontmatter.dumps(markdown))
                fh.write("\n")


if __name__ == "__main__":
    main()
