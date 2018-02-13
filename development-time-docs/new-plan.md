0. Make taxonomy, series core modules as they should not have any dependency. Config has attribute by them.
    (text is not a core module, instead, it is default module)
1. Call attributes instead of frontmatters.

2. Pagination url must start with "_" from root (url). The format will be:
    _/content_url/pagination_no
    
    * _/ will be marked as reserved system url, anything starts with _ is not a problem, but _/ is.
    
    This will help lazy evaluate pagination and dynamic content generation
    for dev server.
    
3. New shell > base shell done > synamic shell interfaced > need to hook up.

4. Static files will be saved according to the directory or or associated content url

5.  -*--
    (texts:: tags in 'x') // (texts:: tags not in z)
    
    vs
    
    texts | title length > 1 | title contains "yo yo" | tags contains ["done", ["complete]] | title startswith "no no" | limit 20 | offset 2 | id > 6 | from 2 5 | first 5 | last 1
    
    -*--
    
    
------------
    
* A data service is needed - for json, yaml, synamicml, etc*

* filtering system improvement for tags, cats etc *

* thumbnail generation *

* routes caching system *