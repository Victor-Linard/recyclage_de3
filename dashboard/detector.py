from torchvision import datasets, transforms, models
import torch
import pillow_heif
import cv2
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch import optim
from PIL import Image
from PIL import Image
from pillow_heif import register_heif_opener
from math import floor
import json
import os
import certifi
import urllib

os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()


# Define model - ref CNN2


def to_device(data, device):
    """Move tensor(s) to chosen device"""
    if isinstance(data, (list, tuple)):
        return [to_device(x, device) for x in data]
    return data.to(device, non_blocking=True)


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


class DeviceDataLoader:
    """Wrap a dataloader to move data to a device"""

    def __init__(self, dl, device):
        self.dl = dl
        self.device = device

    def __iter__(self):
        """Yield a batch of data after moving it to device"""
        for b in self.dl:
            yield to_device(b, self.device)

    def __len__(self):
        """Number of batches"""
        return len(self.dl)


class MyModel:

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
                self.net.load_state_dict(
                    torch.load(self.weights, map_location=lambda storage, loc: storage)["state_dict"])
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
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]), ])
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


def render_prediction(index):
    stridx = str(index)
    classname = 'Unknown'
    if img_class_map is not None:
        if stridx in img_class_map is not None:
            classname = img_class_map[stridx]

    return classname


model = MyModel('cnn2.pth', 'cpu')
CLASS_MAPPING = ['metal', 'plastic', 'cardboard', 'paper', 'trash', 'glass']
COLORS = np.random.uniform(0, 255, size=(len(CLASS_MAPPING), 3))

img_class_map = None
with open('index_to_name.json') as f:
    img_class_map = json.load(f)

for img in ['IMG_6416.JPG', 'IMG_8102.HEIC', 'IMG_8103.HEIC', 'IMG_8105.HEIC', 'IMG_8106.HEIC', 'IMG_8107.HEIC']:
    register_heif_opener()

    inference, confidence = model.infer(img)
    class_name = render_prediction(inference)
    # make a percentage with 2 decimal points
    confidence = floor(confidence * 10000) / 100

    print(f'{img} - {class_name[0]} : {confidence}')
