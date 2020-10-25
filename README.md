# day-one-to-markdown

Convert [Day One](https://dayoneapp.com) journal entries to [Markdown](https://daringfireball.net/projects/markdown) and [Front Matter](https://jekyllrb.com/docs/front-matter/).

## Introduction

Over the years, I've written many posts in [Day One](https://dayoneapp.com); it's a great journaling tool and is lightweight enough to encourage me to write. Unfortunately, it's not easy to pull _all_ the data out in a portable way.

`day-one-to-markdown` converts Day One's zipped JSON exports containing one or more journal entries, to a folder of Markdown files (with Front Matter) and attachments, suitable for use with blogging tools like [Jekyll](https://jekyllrb.com).

## Installation

```bash
git clone git@github.com:jbmorley/day-one-to-markdown.git
cd day-one-to-markdown
pipenv install
```

