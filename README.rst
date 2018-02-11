Synamic
=======

An advanced web application generator that has performance of Static
sites and behavior of Dynamic web applications.

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

    synamic

You will get the synamic shell. To initialize your project, run the
following command:

::

    init

It will create the directory and the necessary startup files for you.

Directory structure:

1. *content*: primarily for keeping your markdown contents (by default
   with .md and .markdown extension). All other files will be considered
   as static files, except for the files that start with a dot (.)-
   files end with ``.meta.txt`` are meta files (primarily for configuration purpose). ``.filename.meta.txt`` are for file meta and ``.meta.txt`` are for directory meta.
2. *static*: for static files.
3. *models*: for models. Currently you should define the default model
   with file name: ``text.model.txt``
4. *templates*: for storing templates. By default the template engine
   will be jinja2
5. *settings.txt*: this file will hold project/site wide settings.
6. *.synamic*: an empty that helps synamic recognize that this is a
   synamic project.

Building a Project
------------------

Open your command line in the synamic project directory, start the
synamic shell and run the ``build`` command.

::

    build

Starting the Development Server
-------------------------------

Open your command line in the synamic project directory, start the
synamic shell and run the ``serve`` command.

::

    serve

This will start a development server with which you can preview you work
live on the browser. Unlike ``build`` this does not generate any output
file.

Template Tag: geturl
--------------------

*Argument Format*: what:type:value

Example:

::

    {% geturl 'static:file:logo.png' %}

    {% geturl 'content:id:home-en' %}

--------------

The maniac behind Synamic is Md. Sabuj Sarker who has one decade+ of
experience and expertise in computer programming. Do not hesitate to
contact him for hiring him for software development, writing, or
training - he will be happy to help you. You can visit his website at
`www.sabuj.me`_

.. _www.sabuj.me: http://www.sabuj.me