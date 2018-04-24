from synamic.core.query_systems.filter_functions import query_by_objects
from synamic.core.services.content.pagination import Pagination
from synamic.core.services.content.functions.create_auxiliary_marked_content import content_create_auxiliary_marked_content


def content_paginate(synamic, contents, starting_content, filter_txt, contents_per_page=2):
    rules_txt = filter_txt
    per_page = contents_per_page
    cnts = query_by_objects(contents, rules_txt)
    aux_contents = []

    paginations = []
    paginated_contents = []

    if cnts:
        q, r = divmod(len(cnts), per_page)
        divs = q
        if r > 0:
            divs += 1

        for i in range(divs):
            _cts = []
            for j in range(per_page):
                idx = (i * per_page) + j  # (row * NUMCOLS) + column        #(i * divs) + j
                if idx >= len(cnts):
                    break
                _cts.append(cnts[idx])
            paginated_contents.append(tuple(_cts))

    if paginated_contents:
        i = 0
        prev_page = None
        for _page_contents in paginated_contents:

            pagination = Pagination(len(paginated_contents), _page_contents, i, per_page)
            paginations.append(pagination)

            if i == 0:
                # setting pagination to the host content
                starting_content._set_pagination(pagination)
                pagination.host_page = starting_content
                prev_page = starting_content

            else:
                aux = content_create_auxiliary_marked_content(
                    synamic,
                    starting_content, pagination.position
                )
                # setting pagination to an aux content
                aux._set_pagination(pagination)
                pagination.host_page = aux

                pagination.previous_page = prev_page
                # TODO: content wrapper for prev/next page : done but it is still not in contract
                prev_page.pagination.next_page = aux
                prev_page = aux

                aux_contents.append(aux)
            i += 1
    return tuple(aux_contents)
