import os
from time import time
import numpy as np
from skimage.metrics import structural_similarity as ssim
import cv2
from django.shortcuts import render
from . import forms
from django.views.decorators.http import require_GET, require_http_methods
import pillow_heif
from PIL import Image
from pillow_heif import register_heif_opener


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
    return render(request, 'dashboard.html', context={'form': forms.UploadPictureToAnalyze})


def mse(image_a, image_b):
    err = np.sum((image_a.astype("float") - image_b.astype("float")) ** 2)
    err /= float(image_a.shape[0] * image_a.shape[1])
    return err


def resize_picture(anonyme_id):
    most_little = 0
    little_img_cv2 = None
    little_img = ''
    for i, img in enumerate(os.listdir('UPLOADED_IMAGES/' + anonyme_id + '/')):
        img_cv2 = cv2.imread('UPLOADED_IMAGES/' + anonyme_id + '/' + img)
        size = img_cv2.shape[0] * img_cv2.shape[1]
        if i == 0:
            most_little = size
            little_img_cv2 = img_cv2
            little_img = img
        if size < most_little:
            most_little = size
            little_img = img
            little_img_cv2 = img_cv2

    for img in os.listdir('UPLOADED_IMAGES/' + anonyme_id + '/'):
        if img != little_img:
            img_cv2 = cv2.imread('UPLOADED_IMAGES/' + anonyme_id + '/' + img)
            img_cv2 = cv2.resize(img_cv2, (little_img_cv2.shape[1], little_img_cv2.shape[0]))
            cv2.imwrite('UPLOADED_IMAGES/' + anonyme_id + '/'+img, img_cv2)


def convert_heic(anonyme_id):
    register_heif_opener()
    for img in os.listdir('UPLOADED_IMAGES/'+anonyme_id+'/'):
        if 'HEIC' in img.upper():
            heic_to_png('UPLOADED_IMAGES/' + anonyme_id, img.upper())


def is_already_compared(already_compared, img1, img2):
    for img_list in already_compared:
        if img1 in img_list and img2 in img_list:
            return True
    return False


def check_for_duplicate(anonyme_id):
    already_compared = []
    for img1 in os.listdir('UPLOADED_IMAGES/'+anonyme_id):
        for img2 in os.listdir('UPLOADED_IMAGES/'+anonyme_id):
            if img1 != img2 and not is_already_compared(already_compared, img1, img2):
                already_compared.append([img1, img2])
                img1_pil = cv2.imread('UPLOADED_IMAGES/'+anonyme_id+'/'+img1)
                img2_pil = cv2.imread('UPLOADED_IMAGES/'+anonyme_id+'/'+img2)

                ssim_res = ssim(img1_pil, img2_pil, channel_axis=-1)
                if ssim_res >= 0.90:
                    os.remove('UPLOADED_IMAGES/'+anonyme_id+'/'+img1)


def heic_to_png(path, img):
    heif_file = pillow_heif.open_heif(path+'/'+img, convert_hdr_to_8bit=False)
    heif_file.convert_to("BGRA;16" if heif_file.has_alpha else "BGR;16")
    np_array = np.asarray(heif_file)
    os.remove(path+'/'+img)
    img = img.split('.HEIC')[0] + ".png"
    cv2.imwrite(path+'/'+img, np_array)


def handle_uploaded_file(files, anonyme_id):
    for file in files:
        save_dir = 'UPLOADED_IMAGES/' + anonyme_id + '/' + anonyme_id + '_' + file.name
        os.makedirs(os.path.dirname(save_dir), exist_ok=True)
        with open(save_dir, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
