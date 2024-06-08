from django.conf import settings
from django.http import FileResponse,HttpResponseBadRequest
from urllib.parse import unquote
import mimetypes
import os
def check_file_extension(filename):
    if filename.endswith((".pdf", ".doc", ".docx")):
        return True
    else:
        return False

def serve_media(request, path):

    result=check_file_extension(path)
    if result and request.user.is_authenticated:
        mimetype, encoding = mimetypes.guess_type(path, strict=True)
        if not mimetype:
            mimetype = "text/html"
       
        file_path = unquote(os.path.join(settings.MEDIA_ROOT, path)).encode("utf-8")
        
        return FileResponse(open(file_path, "rb"), content_type=mimetype)

    else:
        if not os.path.exists(f"{settings.MEDIA_ROOT}/{path}")  :
            return HttpResponseBadRequest("No file found")
        
        if not result:
            mimetype, encoding = mimetypes.guess_type(path, strict=True)
            if not mimetype:
                mimetype = "text/html"
        
            file_path = unquote(os.path.join(settings.MEDIA_ROOT, path)).encode("utf-8")
        
            return FileResponse(open(file_path, "rb"), content_type=mimetype)
        else:
            return HttpResponseBadRequest("restricted")
        