import slimmer
from django.http import HttpResponse

class CompressHtmlMiddleware(object):

    def process_response(self, request, response):
        "compress html response with slimmer"
        if isinstance(response, HttpResponse) and \
            response.get('Content-Type',None).find('text/html;')==0:
            response.content = slimmer.xhtml_slimmer(response.content)
        return response
