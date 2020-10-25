# day-one-to-markdown

Convert [Day One](https://dayoneapp.com) journal entries to [Markdown](https://daringfireball.net/projects/markdown) and [Front Matter](https://jekyllrb.com/docs/front-matter/).

## Introduction

[Day One](https://dayoneapp.com) doesn't make it easy to pull _all_ journal data out in a portable way.

`day-one-to-markdown` converts Day One's zipped JSON exports containing one or more journal entries, to a folder of Markdown files (with Front Matter) and attachments, suitable for use with blogging tools like [Jekyll](https://jekyllrb.com). All of the journal metadata ends up in Front Matter, so it's immediately available to any page template.

## Installation

```bash
git clone git@github.com:jbmorley/day-one-to-markdown.git
cd day-one-to-markdown
pipenv install
```

