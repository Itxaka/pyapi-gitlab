# -*- coding: utf-8 -*-
import warnings

from six.moves.urllib.parse import quote_plus


def deprecated(func):
    """
    This is a decorator which can be used to mark functions as deprecated. It will result in a warning being emitted
    when the function is used.

    :param func: The function to run
    :return: function
    """
    def deprecation_warning(*args, **kwargs):
        warnings.warn('Call to deprecated function {name}. Please consult our documentation at '
                      'http://pyapi-gitlab.readthedocs.io/en/latest/#gitlab.Gitlab.{name}'.format(name=func.__name__),
                      category=DeprecationWarning)
        return func(*args, **kwargs)
    deprecation_warning.__name__ = func.__name__
    deprecation_warning.__doc__ = func.__doc__
    deprecation_warning.__dict__ = func.__dict__
    return deprecation_warning


def format_string(string):
    """
    Formats a string so its ready for Gitlab or returns an int

    :param string: String to be formatted
    :return: Int or String
    """
    if isinstance(string, str):
        return quote_plus(string)
    return string
