#################
Coding Styleguide
#################

This guide summarizes how we MONK developers think the source code should be
formatted. Consider these *guidelines* as advice rather then as law. Sometimes
you might hit a point, where the current version of the document can't help
you. In this you can do the following:

 #. Look into the newest version of this document, if there are any
    meaningful changes for your situation. Also consider building the docs
    yourself.

 #. Look into `PEP-008`_, the official styleguide for the Python core
    development. The whole Python Core project is of course a lot bigger then
    MONK and maybe you can find something there, that wasn't adressed in MONK
    yet. Comment that part of the code and explain why you couldn't follow
    the MONK style guide. If possible create an `Issue`_ and try to get the
    styleguide changed accordingly.

 #. Discuss with other developers if there might be a way that you simply
    didn't know or find yet.

 #. Do what makes most sense in your context. Comment the code extensively and
    find meaningfull ways to tell ``pylint`` and other tools that this line is
    treated specially.


**********
In General
**********

 * Avoid features specific to your python binary. That includes your language
   version as well as the interpreter you are using, i.e. CPython, Jython or
   Pypy.
 * Every line should consist of `79 characters`_ at most.
 * All classes should be `New Style Classes`_.
 * Don't use getters/setters. Use `properties`_ instead.
 * while `comparing singletons`_ like ``None`` always use ``is`` instead of
   ``==``
 * When overwriting comparator functions like ``__eq__``, overwrite all.
 * Every function consists of 30 statements and 12 branches at most.
 * Use the ``with`` clause to open context managers, i.e. when you use 
   :py:func:`open()`.
 * Write your code as type independent as possible, since we should reap the
   `benefits of dynamic typing`_ while using it. E.g. use "`duck testing`_".
 * Use :py:func:`isinstance()` over :py:func:`type()` comparisons, because it
   also `checks for inheritance`_.
 * When checking for emptyness of lists, consider that empty lists are already
   `False`. There is no need to `check for their length`_.
 * Don't check for the ``True``-ness of a value explicitely with
   ``if bool_val is True:``, because it is already ``True`` or ``False``. Use
   ``if bool_val:`` instead.
 * Callable Python scripts should always contain a ``main()`` method. This way
   your code will not only be executable by your script but can also be used by
   other python modules which import yours. If you don't include one, and write
   your code directly in the if, then only your script can make use of that
   code, which is not preferred. Example::

        def main():
            print("hello world")

        if __name__ == '__main__':
            main()

**********
Whitespace
**********

In Python whitespace has meaning. Treating whitespace should recieve even more
consideration then in other languages. Whitespace means:

 * (a space character)
 * ``\t`` (a tab character)
 * ``\n`` (a line feed character; typical for most unix-like operating systems)
 * ``\r\t`` (a carriage return character, followed by a line feed character;
   typical for Windows)

Rules:

 * 4 spaces indentation
 * no tabulator characters, only spaces
 * new lines are ``\n`` characters
 * Classes, functions and blocks should be separated by 2 empty lines each.
 * *no whitespace* in params, brackets braces
 * *no whitespace* before commas, semicolons and colons
 * *no whitespace* before ``(`` in function and class headers
 * *no whitespace* before list indexing, e.g. ``list[5], slice[3:4]``
 * *no whitespace* in default param assignments, e.g. ``def function(a=13):``
 * exactly one space around assignments/operators
 * not more then one statement per line


A complete example of correct whitespacing::

    def function(a, b=5):
        my_list[b] = a
        print(my_list[2:3])


    def another_function(d, e):
        f = d + e
        function(a=f, b=e)


******
Naming
******

Files, folders, modules, classes, functions and attributes all need to be named
in the following fashion:

 * files, folders, modules, packages: ``all_lower_case``
 * variables: ``all_lower_case``
 * global vars: ``all_lower_case``
 * constants: ``ALL_UPPER_CASE``
 * classes: ``BigCamelCase``
 * functions, methods: ``all_lower_case``
 * naming something with a leading underscore makes it considered soft private,
   e.g. ``_like_javas_protected``
 * naming something with two leading underscores, makes it private, i.e. only
   usable inside this class. E.g. ``__only_for_me``
 * surrounding with double underscores should be avoided, since Python itself
   uses this convention for special names, e.g. ``something.__doc__``
 * for referencing the object that calls a method, use ``self``
 * for referencing the class in class functions, use ``cls``

***************
Files - Modules
***************

 * Files are to be encoded in ``utf-8``.
 * Every file starts with the following 2 lines. The first line calls the
   python binary like you would from the shell. This way it is possible to use
   the script in a virtual environment. The second line tells different tools
   about the expected encoding of this file. Example:::

        #!/usr/bin/env python
        # -*- encoding: utf-8 -*-

 * Following these there is an empty line followed by the copyright and
   licensing text.
 * After these general information comes the module docstring.
 * The docstring is followed by the imports in the order:
    * general imports from the Python standard library
    * imports from frameworks
    * imports from your own project

 * Next are the global variables and constants, if necessary (they are
   discouraged all together)
 * Now comes the main part with the class
 * If required, a ``main()`` function comes under the class.
 * In the end is the call of the ``main()`` function::

        if __name__ == '__main__':
            main()

********
Comments
********

In general it is best to write code as self-explanatory as possible. Yet
sometimes you can't get around writing comments, to make things clear. Here are
some situations in which you *should* write a comment:

 * Each module, class and function needs to be accompanied by a `docstring`_.
 * when you wrote code that can't be understood without explanation (although
   you should probably refactor the code instead)
 * when you want pylint or other static code checkers to ignore a piece of code
   that violates the existing coding style
 * when you took a sizable piece of code from a book or a website, referenece
   the source (and check the license of that code)
 * referencing depencies between code parts, which might not be obvious. This
   is critical, if someone wants to debug one side or the other, which might
   introduce new bugs caused by unknown dependencies.

Comments itself must also be written uniformly. Therefore you should follow
these requirements when writing a comment:

 * each comment is written in English
 * each comment describes something underneath, excepting docstrings which also
   partly describe what's above them, i.e. in function doc strings
 * or to say it the other way around: comments are not appended to a line of
   code, instead they are written above the line that should be described::

        #good comment about do_something
        do_something(1,2,3) #bad comment about do_something
        #bad comment about do_something

 * exceptions to this are docstrings which are usually direct underneath of
   what is to be described::

        class Something(object):
        """this is a docstring.
        
        It's directly underneath the class definition
        """
            def __init__(self):
                """this is also a docstring.
                
                It's directly underneath the method definition
                """

                #this is not a docstring, so it stands above it's target
                do_something(4,5,6)

 * each comment is indented as the text underneath, *not* as the text above
   it. The reason is that indented text is treated as *inside* a function,
   while the next line of the same indention is treated as *outside* the
   definition, as with every other Python code::

        def do_something(*args):
            """This is a good place for the docstring.

            The Python compiler understands that this belongs to the function
            declaration above.
            """

        def do_else():
        """This is a bad place for a docstring.
        
        It won't be even recognised as a docstring.
        """

 * Texts in comments are parsable by the `Sphinx`_ documentation generator.
   This **is** a complicated issue, don't look for a 1 minute solution here!
   Seriously start reading the Sphinx website, if you need to write more then
   one or two lines of documentation!
 * Single line comments begin with a hashtag (``#``) character.
 * multiline comments, including `docstring`_:
    * They start with three double quotes (``"""``) characters.
    * The first line of the comment starts directly afterwards and is treated
      as a short summary by many tools.
    * Newlines are used meaningfully inside and there should be at least one
      between the summary (the first line) and the verbose documentation (the
      rest of the docstring).
    * The commenting text is not followed by an empty line, when finished.
    * The end is a line only consisting of three double quotes (``"""``) 
      characters, the same as the starting line.
    * They should be complete sentences.
    * Short sentences can end without a dot (``.``) character.
    * They should contain descriptions for elements like parameters, as
      `described in the Sphinx Docs`_.
 * Comments for version control systems `should be added` to the
   ``__version__`` magic variable.


*****************
Exceptionhandling
*****************

In most cases exception handling should be done like in any other proper Python
project. Here are some things to consider:

 * Use Exception objects and ``raise`` to initiate exception handling.
 * State the Exception classes explicitly in ``except`` clauses, because
   `explicit is better than implicit`.
 * Minimize the number of lines in ``try`` clauses to avoid
   `Pokemon exception handling`_.
 * In Python it is encouraged to use function parameters as expected instead of
   forcing certain types. If the delivered objects don't have the expected
   capabilities, and you can't find a way around it, then ``raise``
   exceptions::

       def u_gonna_quack(duck):
           """I'm expecting a a duck but don't force it to be one.
           """
           try:
               duck.quack()
           except AttributeError:
               print("the param duck can't quack")

*******
Imports
*******

As stated above, the ``import`` calls should be written below the module
docstring, above the constant/global variable definitiones and have the
following order:

 * general imports from the Python standard library
 * imports from frameworks
 * imports from your own project

Different imports should also be on different lines. An exception to that are
``from abc import x,y,z```, where different imports come from the same source.
This is discouraged for other reasons, though. Instead of
``from abc import x,y,z`` you should better ``import abc`` and use ``abc.x``
later on. This way it's more reasonable where something comes from, even though
it's a little more work writing. Always remember
`explicit is better than implicit`_.

*******
The End
*******

You've read it all. I'm so proud of you!


.. references

.. _PEP-008: http://www.python.org/dev/peps/pep-0008
.. _Issue: https://github.com/DFE/MONK/issues/new
.. _79 characters: https://jamiecurle.co.uk/blog/79-characters-or-less/
.. _docstring: http://www.python.org/dev/peps/pep-0257/#what-is-a-docstring
.. _Sphinx: http://sphinx-doc.org/
.. _described in the Sphinx Docs: http://sphinx-doc.org/domains.html#info-field-lists 
.. _should be added: http://stackoverflow.com/a/459185/131120
.. _properties: http://stackoverflow.com/questions/6618002/python-property-versus-getters-and-setters
.. _comparing singletons: http://stackoverflow.com/questions/2209755/python-operation-vs-is-not
.. _explicit is better than implicit: http://www.python.org/dev/peps/pep-0020/
.. _Pokemon exception handling: http://www.codinghorror.com/blog/2012/07/new-programming-jargon.html
.. _benefits of dynamic typing: http://c2.com/cgi/wiki?BenefitsOfDynamicTyping
.. _duck testing: http://en.wikipedia.org/wiki/Duck_typing#Concept_examples
.. _checks for inheritance: http://stackoverflow.com/a/1549854/131120
.. _check for their length: http://www.python.org/dev/peps/pep-0008/#programming-recommendations
.. _New Style Classes: http://www.python.org/doc/newstyle/
