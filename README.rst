==============
django-slimmer
==============

This module is a django conversion of CheckoutableTemplates Zope package: http://zope.org/Members/peterbe/CheckoutableTemplates

The slimmer is taken directly from the Zope package, with django middleware
and a view decorator added.


Installation ::

    sudo easy_install django-slimmer


Install middleware ::

    'slimmer.middleware.CompressHtmlMiddleware',

Or you can use a view decorator to compress specific views ::
    
    from slimmer.decorator import compress_html

    @compress_html
    def browse(request):
        context = RequestContext(request,{})
        return render_to_response('browse.html',context)

Using the slimmer directly ::

    from slimmer import slimmer
    compressed = slimmer.xhtml_slimmer(html)

