# question_paper/utils.py
import os
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources on the local file system.
    """
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    mUrl = settings.MEDIA_URL       # Typically /media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # If the URI contains the domain (e.g. http://127.0.0.1:8000/media/...)
    # strip it to get the local path
    if uri.startswith('http://') or uri.startswith('https://'):
        from urllib.parse import urlparse
        uri = urlparse(uri).path

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        # In development, try to find in STATICFILES_DIRS if STATIC_ROOT is not set
        relative_path = uri.replace(sUrl, "")
        
        # Try STATIC_ROOT first if it exists
        if getattr(settings, 'STATIC_ROOT', None):
            path = os.path.join(settings.STATIC_ROOT, relative_path)
            if os.path.isfile(path):
                return path
        
        # Then try STATICFILES_DIRS
        for static_dir in getattr(settings, 'STATICFILES_DIRS', []):
            path = os.path.join(static_dir, relative_path)
            if os.path.isfile(path):
                return path
        
        return uri
    else:
        return uri

    # make sure that file exists
    if not os.path.isfile(path):
        return uri

    return path

def render_to_pdf(template_src, context):
    template = get_template(template_src)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="output.pdf"'

    # find the response by the status code
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    
    if pisa_status.err:
        return HttpResponse("Error while generating PDF", status=500)
    return response
