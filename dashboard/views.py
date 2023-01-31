import os
from time import time
import numpy as np
from django.db.models import Sum
from skimage.metrics import structural_similarity as ssim
import cv2
from django.shortcuts import render
from . import forms
from django.views.decorators.http import require_GET, require_http_methods
import pillow_heif
from PIL import Image
from pillow_heif import register_heif_opener
from .models import Dechet


# Create your views here.

@require_http_methods(["GET", "POST"])
def dashboard(request):
    if request.method == 'POST':
        form = forms.UploadPictureToAnalyze(request.POST, request.FILES)
        if form.is_valid():
            anonyme_id = (str(time()) + request.META.get('REMOTE_ADDR')).replace('.', '')
            handle_uploaded_file(request.FILES.getlist('file'), anonyme_id)
            if len(request.FILES.getlist('file')) > 1:
                check_for_duplicate(anonyme_id)
    elif request.method == 'GET':
        recover_data()
    return render(request, 'dashboard.html', context={'form': forms.UploadPictureToAnalyze})


def mse(image_a, image_b):
    err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
    err /= float(image_a.shape[0] * image_a.shape[1])
    return err


def check_for_duplicate(anonyme_id):
    for img1 in os.listdir('UPLOADED_IMAGES/'+anonyme_id):
        for img2 in os.listdir('UPLOADED_IMAGES/'+anonyme_id):
            if img1 != img2:
                register_heif_opener()
                if 'HEIC' in img1.upper():
                    img1 = heic_to_png('UPLOADED_IMAGES/'+anonyme_id, img1.upper())
                if 'HEIC' in img2.upper():
                    img2 = heic_to_png('UPLOADED_IMAGES/'+anonyme_id, img2.upper())

                img1_pil = cv2.imread('UPLOADED_IMAGES/'+anonyme_id+'/'+img1)
                img2_pil = cv2.imread('UPLOADED_IMAGES/'+anonyme_id+'/'+img2)

                img1_pix = img1_pil.shape[0]*img1_pil.shape[1]
                img2_pix = img2_pil.shape[0]*img2_pil.shape[1]

                if img1_pix > img2_pix:
                    img1_pil = cv2.resize(img1_pil, (img2_pil.shape[1], img2_pil.shape[0]), interpolation=cv2.INTER_AREA)
                elif img1_pix < img2_pix:
                    img2_pil = cv2.resize(img2_pil, (img1_pil.shape[1], img1_pil.shape[0]), interpolation=cv2.INTER_AREA)

                ssim_res = ssim(img1_pil, img2_pil, channel_axis=-1)
                print(f"{img1} VS. {img2} : {ssim_res}")


def heic_to_png(path, img):
    heif_file = pillow_heif.open_heif(path+'/'+img, convert_hdr_to_8bit=False)
    heif_file.convert_to("BGRA;16" if heif_file.has_alpha else "BGR;16")
    np_array = np.asarray(heif_file)
    os.remove(path+'/'+img)
    img = img.split('.HEIC')[0] + ".png"
    cv2.imwrite(path+'/'+img, np_array)
    return img


def handle_uploaded_file(files, anonyme_id):
    for file in files:
        print(file)
        save_dir = 'UPLOADED_IMAGES/' + anonyme_id + '/' + anonyme_id + '_' + file.name
        os.makedirs(os.path.dirname(save_dir), exist_ok=True)
        with open(save_dir, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)


def recover_data():
    tonnage_total_region_annee_type = Dechet.objects.values('ANNEE', 'C_REGION', 'C_TYP_REG_DECHET').annotate(tonnage_total=Sum('TONNAGE_T'))
    tonnage_total_annee_type = Dechet.objects.values('ANNEE', 'C_TYP_REG_DECHET').annotate(tonnage_total=Sum('TONNAGE_T'))
    print(tonnage_total_annee_type)
    print(tonnage_total_region_annee_type)