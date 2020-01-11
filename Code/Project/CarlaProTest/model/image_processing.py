"""
Use Pytorch to train the model with SYNTHIA-Dataset
and test the Trained model, dann use it with our images

source: https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html
source: https://carla.readthedocs.io/en/latest/python_api/#carlaboundingbox-class
"""
import os
import sys
import glob
import numpy as np
import torch
import json
from pathlib import Path
from PIL import Image

try:
    sys.path.append(glob.glob('../carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass


# preprocessing image with carla does'nt work as well;
# importing the Image-class from carla-Library cause an RuntimeError
# because 'the class cannot be instantiated from Python'
# alternativ: use PIL-Library or OpenCV

# from carla import Image, ColorConverter, SensorData, BoundingBox


class CustumCarlaDataset(object):
    def __init__(self):
        self.root_dir = Path('../gui/Files/Original/')
        self.root = os.listdir(self.root_dir)
        # Load all images and json files, sort them ensuring that they are aligned
        self.imgs = list(
            sorted(f for f in self.root if f.endswith('.png'))
        )
        self.jsons = list(
            sorted(j for j in self.root if j.endswith('.json'))
        )
        pass

    def show(self):
        # print(self.imgs)
        # print(self.jsons)
        tmp_img = self.root_dir / self.imgs[-1]
        print(tmp_img)

        j_file = self.root_dir / self.jsons[-1]
        content = j_file.read_text()
        tmp_json = json.loads(content, encoding='utf-8')
        print(tmp_json['img_specs'])
        img = Image.open(tmp_img)
        # img.frame = 429
        # img.width = tmp_json['img_specs']['width']
        # img.height = tmp_json['img_specs']['height']
        # img.fov = tmp_json['img_specs']['fov']

        print(j_file)
        print(tmp_json)
        print(tmp_img)

        print(img)

    def img_print(self):
        pass


if __name__ == '__main__':
    test = CustumCarlaDataset()
    test.show()
