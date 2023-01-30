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
from math import floor
import json
from torchvision import datasets, transforms, models
import torch
import torch.nn as nn
import json
import os
import certifi

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


def detect_type_of_waste(anonyme_id):
    model = Model('./dashboard/cnn2.pth', 'cpu')
    CLASS_MAPPING = ['metal', 'plastic', 'cardboard', 'paper', 'trash', 'glass']
    COLORS = np.random.uniform(0, 255, size=(len(CLASS_MAPPING), 3))

    for img in os.listdir('UPLOADED_IMAGES/' + anonyme_id):
        inference, confidence = model.infer('UPLOADED_IMAGES/' + anonyme_id+'/'+img)
        class_name = render_prediction(inference)
        confidence = floor(confidence * 10000) / 100

        print(f'{img} - {class_name[0]} : {confidence}')
        return []


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        # Use a pretrained model
        self.network = models.resnet50(pretrained=True)
        # Replace last layer
        num_ftrs = self.network.fc.in_features
        self.network.fc = nn.Linear(num_ftrs, 6)

    # def forward(self, x):
    # x = F.relu(self.conv1(x))
    # x = F.max_pool2d(x, 2, 2)
    # x = self.conv1_bn(x)
    # x = F.relu(self.conv2(x))
    # x = F.max_pool2d(x, 2, 2)
    # x = x.view(-1, 2048)
    # x = F.relu(self.fc1(x))
    # x = self.dropout(x)
    # x = self.fc2(x)
    # x = x.view(-1, 1, 512)
    # x = self.bn(x)
    # x = x.view(-1, 512)
    # x = self.fc3(x)
    # x = self.fc4(x)

    # return x

    def forward(self, xb):
        return torch.sigmoid(self.network(xb))


class Model:

    def __init__(self, trained_weights: str, device: str):
        self.net = Net()
        self.weights = trained_weights
        self.device = torch.device('cuda:0' if device == 'cuda' else 'cpu')
        self._initialize()

    def _initialize(self):
        # Load weights
        try:
            # Force loading on CPU if there is no GPU
            if not torch.cuda.is_available():
                self.net.load_state_dict(torch.load(self.weights, map_location=lambda storage, loc: storage)["state_dict"])
            else:
                self.net.load_state_dict(torch.load(self.weights)["state_dict"])

        except IOError:
            print("Error Loading Weights")
            return None
        self.net.eval()

        # Move to specified device
        self.net.to(self.device)

    def infer(self, path):
        img = Image.open(path).convert('RGB')

        preprocess = transforms.Compose([
            transforms.Resize((300, 300)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),])
        image_tensor = preprocess(img)

        # create a mini-batch as expected by the model
        input_batch = to_device(image_tensor.unsqueeze(0), self.device)

        with torch.no_grad():
            output = self.net(input_batch)

        confidence, index = torch.max(output, dim=1)

        """label = "{}: {:.2f}%".format(CLASS_MAPPING[idx], confidence * 100)
        cv2.rectangle(img, (startX, startY), (endX, endY), COLORS[idx], 2)
        y = startY - 15 if startY - 15 > 15 else startY + 15
        cv2.putText(img, label, (startX, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)"""

        return index[0].item(), confidence[0].item()


def to_device(data, device):
    """Move tensor(s) to chosen device"""
    if isinstance(data, (list, tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)


def render_prediction(index):
    img_class_map = None
    with open('dashboard/index_to_name.json') as f:
        img_class_map = json.load(f)
    stridx = str(index)
    classname = 'Unknown'
    if img_class_map is not None:
        if stridx in img_class_map is not None:
            classname = img_class_map[stridx]

    return classname