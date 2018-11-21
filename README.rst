Synamic
=======

An advanced hybrid (static+dynamic) web application framework, library and tool.

It can be used as:

-  Framework
-  Library
-  Tool

*Powerful, Extensible, Dynamic*

--------------

How To Install
--------------

::

    pip install synamic

Creating a Project
------------------

Choose or create a directory in which you want to keep your templates,
models, contents, static files and other data. Start your command line
in the chosen directory or cd into it. Run the following command:

::

    synamic init

It will create the directory and the necessary startup files for you along with a .gitignore.

Directory structure:

1. *contents*: primarily for keeping your markdown contents (by default
   with .md and .markdown extension). All other files will be considered
   as static files, except for the files that start with a dot (.) or underscore (_).
   Files named ``.meta.syd`` are meta files (primarily for configuration purpose). Instead of putting configurations/fields repeatedly
   in markdown files you can put them in a .meta.syd file. All the markdown files in the .meta.syd's directory or any directory below
   will include fields from it. Meta files in directories below the will be able to override fields from parent metas.
   You can remark .meta.syd as a compile time dependency.
2. *metas*: all the meta folders and files will live inside of this directory. It will contain data, users, markers, models, and menus. More can be added in future.
3. *templates*: for storing templates. By default the template engine
   will be jinja2
4. *settings.syd*: this file will hold project/site wide settings. Create *settings.private.syd* to override settings that you do not want to share with your team or do not want to keep in version control.
5. *sites*: Yes, synamic has multi site feature. A site is a complete sandbox that will have different templates, metas, contents, etc.
   Even it can have sub-sites under it. A site can inherit many things from its parent sites.

If you prefer to work inside the synamic shell, you can start it with the following command.

::

    synamic shell



Building a Project
------------------

Run the following command from the project's root directory.

::

    synamic build

You will get your site(s) build under the *_outputs* directory. You can also run the same command from synamic shell where you will not need to precede the 'build' command with 'synamic'.

Starting the Development Server
-------------------------------

Open your command line in the synamic project directory, start the
synamic shell and run the ``serve`` command.

::

    serve

To run the server without the synamic shell use the following command.

::

    synamic serve

This will start a development server with which you can preview you work
live on the browser. Unlike ``build`` this does not generate any output
file.

Template Tag: geturl
--------------------

*Argument Format*: synamic_scheme://type:value

Example:

::

    {% getc 'url://file:logo.png' %}

    {% getc 'url://id:home-en' %}

--------------

The maniac behind Synamic is Md. Sabuj Sarker who has one decade+ of
experience and expertise in computer programming. Do not hesitate to
contact him for hiring him for project management, software development, writing, or
training - he will be happy to help you. You can visit his website at
`www.sabuj.me`_

.. _www.sabuj.me: http://www.sabuj.me