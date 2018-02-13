# Path and PathTree

- Every file can have a meta file with the extension `.meta` or `meta.yaml` (final decision will be taken later)

# Add optional parameter to `get_module_paths` on PathTree
At this point modules only could get all paths from it's directory and filter that itself.
For taxonomy module a new requirement has appeared. It is necessary to list path by `single, multiple, hierarchical` to detect that the content files are of different types.

The extra parameter should be `*starting_path`:
Let's say, I want to get all the paths from `multiple/tags` inside taxonomy module. So, I would call it like this:

- <s>`get_module_paths(mod_obj, 'multiple', 'tags')`

OR
</s>

- `get_module_paths(mod_obj, 'multiple/tags')`

OR

- `get_module_paths(mod_obj, r'multiple\tags')`

*Note:* as the syntax `*starting_path` indicates you can provide multiple paths.

*The first way is the best way to go*
