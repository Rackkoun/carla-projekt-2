import os
from pathlib import Path
import cv2 as cv
import json


class CUSANIDatasetManger(object):
    original_img_path = Path('../res/img/originals/')
    edited_img_path = Path('../res/img/edited/')
    jsons_path = Path('../res/img/jsons/')
    IMG_LST = None
    JSON_LST = None

    @staticmethod
    def _load_dataset():
        img_path = os.listdir(CUSANIDatasetManger.original_img_path)
        json_path = os.listdir(CUSANIDatasetManger.jsons_path)

        # Load all images and json files, sort them ensuring that they are aligned
        imgs = list(sorted(f for f in img_path))
        jsons = list(sorted(j for j in json_path))
        return imgs, jsons

    @staticmethod
    def load():
        print("loading generated images and files...")
        CUSANIDatasetManger.IMG_LST, CUSANIDatasetManger.JSON_LST = CUSANIDatasetManger._load_dataset()
        print('done!')
        return CUSANIDatasetManger.IMG_LST, CUSANIDatasetManger.JSON_LST

    @staticmethod
    def on_load_img(idx):
        img = cv.imread('{}'.format(CUSANIDatasetManger.original_img_path / CUSANIDatasetManger.IMG_LST[idx]))

        return img, str(CUSANIDatasetManger.IMG_LST[idx])

    @staticmethod
    def on_load_file(idx):
        file_content = (CUSANIDatasetManger.jsons_path / CUSANIDatasetManger.JSON_LST[idx]).read_text()
        json_file = json.loads(file_content, encoding='utf-8')
        return json_file

    @staticmethod
    def rearrang_img_for_gui(arr_img):
        """
        OpenCV read Image color in Blue, Green, Red; the color priority must be rearrange
        (split) before display it with oder Image-library as PIL or ImageTK
        """
        blue, green, red = cv.split(arr_img)
        rearranged_img = cv.merge((red, green, blue))
        return rearranged_img

    @staticmethod
    def dict_to_json_format(data_dict, name):
        path = Path('../res/files/copy/labels')
        file_name = path / 'copy-{}.json'.format(name)
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(data_dict, indent=3, ensure_ascii=False))


##################################################
# -- identify vehicles and pedestrian with OpenCV #
##################################################
class Box2DClass(object):
    """
    Test class for the program
    """

    @staticmethod
    def on_load_file(file_content):
        with open(file_content, encoding='utf-8') as data:
            json_file = json.load(data)
            return json_file

    @staticmethod
    def get_objs(dico):
        vehicles = dico['object_1']
        pedestrians = dico['object_2']
        return vehicles, pedestrians

    @staticmethod
    def identity_pedestrians(ima, pedestrians_dico):
        # draw rectangle
        for point in pedestrians_dico['identify']:
            box_img = cv.rectangle(
                ima,
                (point['P0'], point['P1']),
                (point['P2'], point['P3']),
                (0, 255, 0),
                1
            )
            cv.putText(box_img,
                       str(pedestrians_dico['class']),
                       (point['P0'], point['P1'] - 10),
                       cv.FONT_HERSHEY_PLAIN,
                       0.8,
                       (255, 255, 255))

        return ima, len(pedestrians_dico['identify'])

    @staticmethod
    def identity_vehicles(ima, vehicles_dico):
        # draw rectangle
        for point in vehicles_dico['identify']:
            box_img = cv.rectangle(
                ima,
                (point['P0'], point['P1']),
                (point['P2'], point['P3']),
                (0, 0, 255),
                1
            )
            cv.putText(box_img,
                       str(vehicles_dico['class']),
                       (point['P0'], point['P1'] - 10),
                       cv.FONT_HERSHEY_PLAIN,
                       0.8,
                       (255, 255, 255))
        return ima, len(vehicles_dico['identify'])

    @staticmethod
    def identity_all(ima, dico):
        # draw rectangle
        vehicles, pedestrian = Box2DClass.get_objs(dico)
        ima, v_len = Box2DClass.identity_vehicles(ima, vehicles)
        ima, p_len = Box2DClass.identity_pedestrians(ima, pedestrian)

        return ima, v_len, p_len

    @staticmethod
    def on_saving_copy(img, img_name):
        path = Path('../res/img/testcv')
        img_n = path / 'copy-{}'.format(img_name)
        cv.imwrite(str(img_n), img)
        print('Edited ', str(img_name), 'Image saved!')
