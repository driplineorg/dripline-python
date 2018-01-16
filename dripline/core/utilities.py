#!/usr/bin/python

from __future__ import absolute_import

import inspect

__all__ = []

__all__.append('fancy_doc')
def fancy_doc(cls):
    '''
    A function for decorating classes and using inspection to upgrade doc strings.

    This decorator is relatively inflexible as far as input doc string format. The decorated class must havve descriptive content, if any, in the *class* doc string. Then any kwargs to the __init__ function must be listed, one per line, in the doc string to that method (no other content is allowed). Each line should be of the form:
    <kwarg_name> (<kwarg type or types>): <description>

    The decorator will merge the doc kwarg sections for all parent classes and produce a new class of the same name with the same class doc string and combined kwarg doc string
    '''
    classes = inspect.getmro(cls)
    arg_list = []
    for i_cls in classes:
        if i_cls is object:
            pass
        else:
            try:
                this_arg_list = i_cls.__init__.__doc__.lstrip('\n').rstrip(' ').split('\n')
                arg_list += [new_arg for new_arg in this_arg_list if new_arg not in arg_list and new_arg != '']
            except Exception as e:
                pass
    arg_section = '\n    Keyword Args:\n'+'\n'.join(arg_list)
    base_doc = ''
    try:
        base_doc = cls.__doc__.rstrip().split('Keyword Args:')[0]
    except:
        pass
    new_doc = '\n'.join([base_doc, arg_section])
    clsdict = dict(inspect.getmembers(cls))
    clsdict = {'__doc__': new_doc}

    return type(cls.__name__, (cls,), clsdict)
