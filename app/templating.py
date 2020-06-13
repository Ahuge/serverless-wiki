import sys
import markdown2

PAGE_CONTENT_LINE = "<!-- PAGE_CONTENT_HERE -->\n"
PAGE_SOURCE_LINE = "<!-- PAGE_SOURCE_HERE -->\n"
POST_URL_LINE = "<!-- POST_URL -->"


def apply_template(md, post_url):
    with open(sys.path[0] + "/templates/index.html", "r") as template:
        result = ''
        line = template.readline()
        while line:
            if line == PAGE_CONTENT_LINE:
                # TODO further processing, e.g. handling in-wiki links
                # both to existing and non-existing pages.
                result += markdown2.markdown(md)
            elif line == PAGE_SOURCE_LINE:
                result += md
            else:
                result += line.replace(POST_URL_LINE, post_url)
            line = template.readline()
    return result
