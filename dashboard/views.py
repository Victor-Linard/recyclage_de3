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
        tonnage_total_france, tonnage_total_annee_verre, tonnage_total_annee_plastique, tonnage_total_annee_menager, tonnage_total_region_annee_type, diff_tonnage_france_total, tonnage_total_verre, tonnage_total_plastique, tonnage_total_menager = recover_data()
    return render(request, 'dashboard.html', context={'form': forms.UploadPictureToAnalyze, 'tonnage_total_france': round(tonnage_total_france/1000, 3), 'diff_tonnage_total_france' : round(diff_tonnage_france_total, 3), 'tonnage_total_annee_verre' : round(tonnage_total_annee_verre/1000, 3), 'tonnage_total_annee_menager' : round(tonnage_total_annee_menager/1000, 3), 'tonnage_total_annee_plastique' : round(tonnage_total_annee_plastique/1000, 3), 'tonnage_total_verre' : tonnage_total_verre, 'tonnage_total_plastique': tonnage_total_plastique, 'tonnage_total_menager': tonnage_total_menager})


def recover_data():
    tonnage_total_region_annee_type = Dechet.objects.values('ANNEE', 'C_REGION', 'C_TYP_REG_DECHET')\
        .annotate(tonnage_total=Sum('TONNAGE_T'))

    tonnage_total_annee_type = Dechet.objects.values('ANNEE', 'C_TYP_REG_DECHET')\
        .annotate(tonnage_total=Sum('TONNAGE_T'))

    tonnage_total_france = Dechet.objects.values('ANNEE')\
        .annotate(tonnage_total=Sum('TONNAGE_T'))\
        .filter(ANNEE__in=[2017, 2019])

    tonnage_total_france_annne_inf = tonnage_total_france.get(ANNEE=2017).get('tonnage_total')
    tonnage_total_france = tonnage_total_france.get(ANNEE=2019).get('tonnage_total')
    diff_tonnage_france_total = (tonnage_total_france - tonnage_total_france_annne_inf) / tonnage_total_france_annne_inf * 100

    tonnage_total_annee_verre = int(tonnage_total_annee_type\
        .filter(ANNEE=2019, C_TYP_REG_DECHET='08C')\
        .aggregate(Sum('tonnage_total')).get('tonnage_total__sum'))

    tonnage_total_annee_plastique = int(tonnage_total_annee_type\
        .filter(ANNEE=2019, C_TYP_REG_DECHET='08B')\
        .aggregate(Sum('tonnage_total')).get('tonnage_total__sum'))

    tonnage_total_annee_menager= int(tonnage_total_annee_type\
    .filter(ANNEE=2019, C_TYP_REG_DECHET__in=['08A', '08D'])\
    .aggregate(Sum('tonnage_total'))\
    .get('tonnage_total__sum'))

    tonnage_total_verre = [int(item.get('tonnage_total')) for item in
                           sorted(tonnage_total_annee_type.filter(C_TYP_REG_DECHET='08C'), key=lambda x: x.get('ANNEE'))]

    tonnage_total_plastique = [int(item.get('tonnage_total')) for item in
                               sorted(tonnage_total_annee_type.filter(C_TYP_REG_DECHET='08B'), key=lambda x: x.get('ANNEE'))]

    tonnage_total_menager = [int(item.get('tonnage_total')) for item in
                             sorted(tonnage_total_annee_type.filter(C_TYP_REG_DECHET__in =['08A', '08D']), key=lambda x: x.get('ANNEE'))]

    return int(tonnage_total_france), tonnage_total_annee_verre, tonnage_total_annee_plastique, tonnage_total_annee_menager, tonnage_total_region_annee_type, diff_tonnage_france_total, tonnage_total_verre, tonnage_total_plastique, tonnage_total_menager
