Coding Style Guide
==================

This guide summarizes how we :term:`MONK` developers think the source code
should be formatted. Consider these *guidelines* advice rather than law.
Sometimes you might hit a point, where the current version of the document
can not help you. In this case you can do the following:

 #. Check whether the newest version of this document contains any
    changes concerning your situation. Also consider
    :ref:`building the docs yourself<contrib-build>`.

 #. Refer to `PEP-008`_, the official style guide for Python core development.
    The Python Core project is, of course, a lot bigger than :term:`MONK`,
    meaning you might find something there, that has not been addressed in
    :term:`MONK` yet. Place a comment in the code explaining why you were not
    able to follow :term:`MONK's<MONK>` style guide. If possible, create an
    `Issue`_ and try to get the style guide changed accordingly.

 #. Discuss with other developers whether there might be a way that you are not
    aware of.

 #. Do what makes most sense in your context. Use comments extensively and
    find meaningful ways to tell ``pylint`` and other tools that this line is
    to be treated as an exception.


In General
----------

 * Avoid features specific to your Python binary. That includes your language
   version as well as the interpreter you are using, e.g., CPython, Jython, or
   Pypy.
 * Every line should consist of `79 characters`_ at most.
 * No line should contain more than one statement.
 * All classes should be `New Style Classes`_.
 * Do not use getters/setters. Use `properties`_ instead.
 * When `comparing singletons`_ like ``None`` always use ``is`` instead of
   ``==``.
 * When overwriting comparator functions like ``__eq__``, ensure that you
   overwrite all of them.
 * Every function consists of 30 statements and 12 branches at most.
 * Use the ``with`` clause to open context managers, e.g. when you use
   :py:func:`open()`.
 * Write your code as type independently as possible, since we should reap the
   `benefits of dynamic typing`_ while using it. E.g. use "`duck testing`_".
 * Use :py:func:`isinstance()` instead of :py:func:`type()` comparisons
   because it also `checks for inheritance`_.
 * When checking for emptyness of lists, consider that empty lists are already
   `False`. There is no need to `check for their length`_.
 * Do not check for the ``True``-ness of a value explicitely with
   ``if bool_val is True:`` because it is already ``True`` or ``False``. Use
   ``if bool_val:`` instead.
 * Callable Python scripts should always contain a ``main()`` method. This way
   your code will not only be executable by your script but can also be used by
   other Python modules which import yours. If you do not include one, and
   instead put your code directly into the if, then only your script can make
   use of that code, which is not preferred. Example::

        def main():
            print("hello world")

        if __name__ == '__main__':
            main()

Whitespace
----------

In Python whitespace has meaning. Thus, treating whitespace should receive even
more consideration than in other languages. Whitespace means:

 * (a space character)
 * ``\t`` (a tab character)
 * ``\n`` (a line feed character; typical for most Unix-like operating systems)
 * ``\r\n`` (a carriage return character, followed by a line feed character;
   typical for Windows)

Rules:

 * 4 spaces indentation
 * no tabulator characters, only spaces
 * New lines are ``\n`` characters.
 * Classes, functions, and blocks should be separated by 2 empty lines each.
 * *no whitespace* in params, brackets, and braces
 * *no whitespace* before commas, semicolons, and colons
 * *no whitespace* before ``(`` in function and class headers
 * *no whitespace* before list indexing, e.g., ``list[5], slice[3:4]``
 * *no whitespace* in default param assignments, e.g., ``def function(a=13):``
 * exactly one space around assignments/operators


A complete example of correct whitespacing::

    def function(a, b=5):
        my_list[b] = a
        print(my_list[2:3])


    def another_function(d, e):
        f = d + e
        function(a=f, b=e)


Naming
------

Files, folders, modules, classes, functions, and attributes are to be named
in the following fashion:

 * files, folders, modules, packages: ``all_lower_case``
 * variables (including global variables): ``all_lower_case``
 * constants (convention only, not enforced by interpreter): ``ALL_UPPER_CASE``
 * classes: ``BigCamelCase``
 * functions, methods: ``all_lower_case``
 * Naming something with a leading underscore declares it to be soft private
   (e.g. ``_like_javas_protected``).
 * Naming something with two leading underscores makes it private, i.e. only
   usable inside this class (e.g. ``__only_for_me``).
 * Use of double underscores at beginning and end should be avoided, since
   Python itself uses this convention for special names
   (e.g. ``something.__doc__``)
 * Use ``self`` to reference the object calling a method.
 * Use ``cls`` to reference the class in class functions.

Files - Modules
---------------

 * Files are to be encoded using ``utf-8``.
 * Every file starts with the following 2 lines::

        #!/usr/bin/env python
        # -*- encoding: utf-8 -*-

   The first line calls the python binary the way you would from the shell.
   This way it is possible to use the script in a virtual environment. The
   second line tells other tools about the expected encoding of this
   file.
 * Following these there is an empty line followed by the copyright and
   licensing text.
 * After this general information there is the module docstring.
 * The docstring is followed by imports in this order:
    * general imports from the Python standard library
    * imports from frameworks
    * imports from your own project

 * Next are global variables and constants, if necessary (use of them
   is generally discouraged).
 * Next, there is the main part containing the class.
 * If required, the ``main()`` function follows below the class.
 * At the end there is the call of the ``main()`` function::

        if __name__ == '__main__':
            main()

Comments
--------

In general it is best to write code as self-explanatory as possible. Yet
sometimes you cannot get around writing comments to make things clear. Here are
some situations in which you *should* write a comment:

 * Each module, class, and function needs to be accompanied by a `docstring`_.
 * Whenever you find yourself writing code that cannot be understood without
   explanation (although you might want to consider refactoring the code
   instead).
 * If you want pylint or other static code checkers to ignore a piece of code
   that violates the existing coding style.
 * If you took a sizable piece of code from a book or a website, reference
   the source (and be sure to check the license of that code).
 * Reference dependencies between code parts, which might not be obvious.
   This is crucial, if someone wants to make changes on either side, as these
   might introduce new bugs caused by unknown dependencies.

Comments themselves must also be written uniformly. Therefore you should follow
these requirements when writing a comment:

 * Each comment is written in English.
 * Each comment describes something underneath, excepting docstrings which also
   partly describe code that is above them, e.g. in function doc strings.
 * To put it the other way around: comments are not appended to a line of
   code, instead they are written above the line they describe::

        #good comment about do_something
        do_something(1,2,3) #bad comment about do_something
        #bad comment about do_something

 * Exceptions to this are docstrings which usually are directly underneath of
   what is to be described::

        class Something(object):
            """This is a docstring.

            It is put directly underneath the class definition.
            """


            def __init__(self):
                """This is also a docstring.

                It is put directly underneath the method definition.
                """

                #This is not a docstring, thus it is put above its target.
                do_something(4,5,6)

 * Each comment is indented the same way as the text underneath, *not* as
   the text above it. This is because indented text is treated as *inside*
   a function, while the next line of the same indention is treated as
   *outside* the definition, as with every other Python code::

        def do_something(*args):
            """This is the correct way to indent a docstring.

            The Python compiler understands that this belongs to the function
            declaration above.
            """

        def do_else():
        """This is the wrong way to indent a docstring.

        It won't even be recognised as a docstring.
        """

 * Texts in comments are parsable by the `Sphinx`_ documentation generator.
   This can be a complicated issue, so if you encounter any problems,
   do not expect to find a 1 minute solution here! Seriously, start reading
   the Sphinx website, if you need to write more
   than one or two lines of documentation!
 * Single line comments begin with a hash (``#``) character.
 * Multiline comments, including `docstring`_, adhere to the following rules:
    * They start with three straight double quote (``"""``) characters.
    * The first line of the comment starts directly afterwards and is treated
      as a short summary by many tools.
    * Newlines are used meaningfully inside and there should be at least one
      empty line between the summary (the first line) and the verbose
      documentation (the rest of the docstring).
    * The commenting text is not followed by an empty line.
    * The end is marked by a line consisting exclusively of three straight
      double quote (``"""``) characters.
    * They should consist of complete sentences.
    * They should contain descriptions for elements like parameters, as
      `described in the Sphinx Docs`_.
 * Comments for version control systems `should be added`_ to the
   ``__version__`` magic variable.


Exception Handling
------------------

In most cases exception handling should be done like in any other proper Python
project. Here are some things to consider:

 * Use Exception objects and ``raise`` to initiate exception handling.
 * State Exception classes explicitly in ``except`` clauses because
   `explicit is better than implicit`_.
 * Minimize the number of lines in ``try`` clauses to avoid
   `Pokemon exception handling`_.
 * In Python, it is encouraged to use function parameters as expected instead
   of forcing certain types. If the delivered objects do not have the expected
   capabilities and there is no sensible way to handle this, then ``raise``
   exceptions::

       def u_gonna_quack(duck):
           """I'm expecting a duck but don't force it to be one.
           """
           try:
               duck.quack()
           except AttributeError:
               print("The param duck can't quack.")

Imports
-------

As stated above, ``import`` calls should be written below the module
docstring, above the constant/global variable definitions, and in the
following order:

 * general imports from the Python standard library
 * imports from frameworks
 * imports from your own project

Different imports should be on different lines. An exception to this are
statements like ``from abc import x,y,z``, making different imports from
the same source. This is discouraged for other reasons, though. Instead of
``from abc import x,y,z`` you should use ``import abc`` and then refer to
``abc.x`` later on. This way it is easier to identify where something comes
from, even though it requires a little more work typing. Always remember
`explicit is better than implicit`_.

The End
-------

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
