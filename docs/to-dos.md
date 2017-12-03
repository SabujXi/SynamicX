# DONE
1. Resolve content id.
2. Template tags (e.g. url_object resolver tag) 
    - `geturl` is done. 
3. Development server
    Later in road map after initial dev server.
        Dev server should not fail on exception. Instead it should show exceptions and errors in a friendly manner.
    (* very minimal server added *)
    
4. Module name validations.

# TO-DOs

# Random TO DOs

# Draft TO-DOs (not well updated after implementing)
** planning to change url_object name to content_name **

- More Content Modules
    - Redirect
    - Author
    - Archive

- Architectural Change:
    - Content id by file name should be set optional so that other module_object developers can use that feature without coding for that from scratch
    
- Remove directory_name from modules and let name of the module_object do that job.
    I do not want confusion and keep the names the same everywhere.
    And thus it is wise to have the same name everywhere. So, form this to-do implementation there
    will be no directory_name. 
    
    - Also make module_object names singular not plural. It looks odd to refer text id as "tests:2", it sounds far better to refer to that as "text:2"
    - Append 'Module' to module_object classes. ** And thus append 'Content' to the content class of the module_object**. So, Texts becomes TextModule and Text becomes TextContent 

- Add multi language.
    Develop a method (way) of creating different home for them.

- If filename.ext.meta is added beside static files then use that to extract content id and name for that.
    It will help minimize the hassle of referring to the full file name for the complex ones and the hassle will be lot less when the file is inside any deep nested directory.
    Also, in this way we can rename their url_object/file name dynamically.

- paginate with query and chained sort will be a method on config.
    On calling this contents will be dynamically be added to the map.
    THUS: iteration will no longer be done by for, instead I am going to use while loop with dqueue
    
- There should not be content and meta module_object any more.
    When thinking about the whole think I find in the kingdom of my thought and dream that I am using meta modules to add content dynamically to the config.
    So, from now on there will be content and template modules.
- Auto content generation tags, e.g. paginate, will not be able to create content when they are inside dynamically **generated** content.

- Content will have attribute whether they are is_static, is_dynamic, is_auxiliary (e.g. created due to invocation of pagination)
    Static files are static, things from like markdown with body and/or attributes are dynamic, things generated as a result of call from paginate are generated

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
