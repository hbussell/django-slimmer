import slimmer
from django.http import HttpResponse
try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps  # Python 2.3, 2.4 fallback.


def compress_html(view_func):
    """
    Decorator that adds headers to a response so that it will
    never be cached.
    """
    def _wrapped_view_func(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        if isinstance(response, HttpResponse) and \
            response.get('Content-Type',None).find('text/html;')==0:
            response.content = slimmer.xhtml_slimmer(response.content)
        return response
    return wraps(view_func)(_wrapped_view_func)





