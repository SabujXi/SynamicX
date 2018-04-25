from synamic.core.urls.url import ContentUrl


def construct_tag_url(synamic, tag):
    return ContentUrl(synamic, '_/tag/' + tag.id, append_slash=True)
