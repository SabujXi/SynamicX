# DONE
1. Resolve content id.
2. Template tags (e.g. url_object resolver tag) 
    - `geturl` is done. 
3. Development server
    Later in road map after initial dev server.
        Dev server should not fail on exception. Instead it should show exceptions and errors in a friendly manner.
    (* very minimal server added *)
    
4. Module name validations.
5. Front Matter Parsing By Callable Registration
6. Pagination Object
7. Get content id & name from frontmatter, get id from file name - frontmatter gets higher priority
    - ID won't be taken from file name. So, I want to provide the maximum flexibility in naming the files.
    - Instead they are suggested to start the file name with id inside yaml if that is numeric

# TO-DOs

3. Parser/Lexer/Compiler for filter rule parsing


# Random TO DOs

# Draft TO-DOs (not well updated after implementing)
** planning to change url name to content_name **

- More Content Modules
    - Redirect
    - Author
    - Archive
    - Home (for different languages)


- Add multi language.
    Develop a method (way) of creating different home for them.


- Add the following feature:
    Every content directory (the module_object root directory) and the subdirectories
     may have a meta file. That meta file will contain some config, among them 
     a root url_object can be defined. So, whatever .md or files like that are being put there will
     be rendered with that url_object as the prefix.
     Must remember that this root url_object will follow the module_object root url_object if any is defined.

- file change detection and reloading relevant content and url_object

- At last: An editor with the development server
    All dynamic content can be edited dynamically browsing throw content folders, rendered with templates.
    Or they can be edited by the browsing to them clicking the edit button (file upload and delete will also be available)
    *Rules for editing will parsed from the contents*
