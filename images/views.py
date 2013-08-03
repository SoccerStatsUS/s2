from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from images.models import Image

def image_detail(request, image_id):

    image = get_object_or_404(Image, id=image_id)
    
    context = {
        'image': image,
        }

    return render_to_response("images/detail.html",
                              context,
                              context_instance=RequestContext(request)
                              )

