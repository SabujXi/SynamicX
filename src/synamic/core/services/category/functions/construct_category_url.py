from synamic.core.urls.url import ContentUrl


def construct_category_url(synamic, category):
    return ContentUrl(synamic, '_/category/' + category.id)
