# Taxonomy Module

In Synamic, taxonomies are gonna be the thing that classifies contents. Tags and Categories that are being used now will
merge into taxonomies, though they will be written like they are written now in frontmatter except probable separator and escaping change.
  
There will be three kind of taxonomies that are:

- Single 
- Multiple
- Hierarchical

## Single
Single taxonomies will have only one value unlike tags (multiple) and categories (hierarchical).
For example, 'type' can be one single taxonomy. Another can be 'release-year'.
```text
type: book
```

```text
listed: no
```

## Multiple
Tags are one of the best examples of taxonomy of multiple type.

```text
tags: Development, Design, Python
```

## Hierarchical
Categories are the best example of hierarchical taxonomies.

```text
categories: Blog, Python, Book
```
*Note*: Though hierarchical taxonomies look exactly like multiple, e.g. tags, taxonomies, they are different.
The hierarchy will be defined in the categories content files inside `taxonomy-module-directory/hierarchical/category`.
If listed hierarchical terms are not defined there then they will act like multiple. Remember that they can be easily defined like multiple when defined.

## Folder Structure
Content-Modules-Root-Directory
```text
-taxonomy
--single
----type
----date
----etc
--multiple
----tags
----etc
--hierarchical
----categories
----etc
``` 

## Frontmatter Parsing
Taxonomy module will define callable for frontmatter key's value parsing.
For text contents there will be a generic parser.
A frontmatter key to be recognized as a taxonomy of some kind, it should be at least listed inside any of the directories. Listed as what? Folder or file? Ok, I will talk about that later.


## How to Get the Taxonomies 
Content objects and content wrapper objects will have an attached copy of taxonomies.
- It is not necessary to call `content.taxonomy.multiple.tags`. You can directly call it find it by `content.taxonomy.tags` though the preceding method will also be available.
- Taxonomies' keys, e.g. `tags`, `categories`, will also be available on content and content wrappers. The magic will be `__getitem__` to `content.taxonomy` - no extra work needed on the part of the api consumers.

## Doc Writing Log
*I am writing the initial part of this doc before starting to create taxonomy module.*
*It is currently in the plan phase to be executed soon.*
*The first writing is on 07-Dec-2017 10:40PM GMT+6*
*Second update 08-Dec-2017*