"""
    author: "Md. Sabuj Sarker"
    copyright: "Copyright 2017-2018, The Synamic Project"
    credits: ["Md. Sabuj Sarker"]
    license: "MIT"
    maintainer: "Md. Sabuj Sarker"
    email: "md.sabuj.sarker@gmail.com"
    status: "Development"
"""

import re

start_pattern = re.compile(r"^\s*(-{3,})[\n\r]+", re.IGNORECASE | re.DOTALL)
end_pattern = re.compile(r"[\n\r]+(-{3,})[\n\r]+", re.IGNORECASE | re.DOTALL)


def parse_front_matter(text):
    status = True
    front = ""
    body = ""
    start_match = start_pattern.search(text)
    if start_match:
        end_match = end_pattern.search(text, start_match.end())
        if end_match:
            body = text[end_match.end():]
            front = text[start_match.end(): end_match.start()]
        else:
            status = None  # None means, the front matter is corrupted
    else:
        status = False
        body = text

    return status, front, body
    # return {"status": status, "front": front, "body": body}