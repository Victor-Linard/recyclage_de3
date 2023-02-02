from time import time
from django.db.models import Sum
from django.shortcuts import render
from capture_image import forms
from django.views.decorators.http import require_GET, require_http_methods
from .models import Dechet
import os
import certifi
from capture_image.views import handle_uploaded_file, detect_type_of_waste, convert_heic, resize_picture, check_for_duplicate

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()


# Create your views here.

@require_http_methods(["GET", "POST"])
def dashboard(request):
    if request.method == 'POST':
        form = forms.UploadPictureToAnalyze(request.POST, request.FILES)
        if form.is_valid():
            anonyme_id = (str(time()) + request.META.get('REMOTE_ADDR')).replace('.', '')
            handle_uploaded_file(request.FILES.getlist('file'), anonyme_id)
            convert_heic(anonyme_id)
            if len(request.FILES.getlist('file')) > 1:
                resize_picture(anonyme_id)
                check_for_duplicate(anonyme_id)
            detect_type_of_waste(anonyme_id)
    elif request.method == 'GET':
        recover_data()

    return render(request, 'dashboard.html', context={'form': forms.UploadPictureToAnalyze})


def recover_data():
    tonnage_total_region_annee_type = Dechet.objects.values('ANNEE', 'C_REGION', 'C_TYP_REG_DECHET').annotate(tonnage_total=Sum('TONNAGE_T'))
    tonnage_total_annee_type = Dechet.objects.values('ANNEE', 'C_TYP_REG_DECHET').annotate(tonnage_total=Sum('TONNAGE_T'))
    print(tonnage_total_annee_type)
    print(tonnage_total_region_annee_type)
