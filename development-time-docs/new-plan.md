0. Make taxonomy, series core modules as they should not have any dependency. Config has attribute by them.
    (text is not a core module, instead, it is default module)
1. Call attributes instead of frontmatters.

2. Pagination url must start with "_" from root (url). The format will be:
    _/content_url/pagination_no
    
    This will help lazy evaluate pagination and dynamic content generation
    for dev server.
    
3. New shell

4. Static files will be saved according to the directory or or associated content url
