import os

from django.shortcuts import render
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.temp import NamedTemporaryFile
from .models import Image
from django.shortcuts import redirect
import urllib.request
from time import time
from dashboard.views import handle_uploaded_file, detect_type_of_waste

# Create your views here.


def capture_image(request):
    if request.method == 'POST':
        image_path = request.POST["src"]
        anonyme_id = (str(time()) + request.META.get('REMOTE_ADDR')).replace('.', '')
        image = NamedTemporaryFile()
        image.write(urllib.request.urlopen(image_path).read())
        image.flush()
        image = File(image)
        image.name = anonyme_id + '.jpg'
        if image is not None:
            os.makedirs(os.path.dirname('./UPLOADED_IMAGES'), exist_ok=True)
            obj = Image.objects.create(anonyme_id=anonyme_id, image=image)
            obj.save()
            detect_type_of_waste()
            obj.delete()
            os.remove('UPLOADED_IMAGES/'+image.name)
        else:
            return redirect('/dashboard')
        return redirect('/dashboard')
    return render(request, 'capture_image.html', context={})
