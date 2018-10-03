from synamic.core.services.urls.url import ContentUrl


def construct_category_url(synamic, category):
    return ContentUrl(synamic, '_/category/' + category.id, append_slash=True)
