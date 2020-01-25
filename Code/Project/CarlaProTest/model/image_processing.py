"""
Use Pytorch to train the model with SYNTHIA-Dataset
and test the Trained model, dann use it with our images

source: https://pytorch.org/tutorials/intermediate/torchvision_tutorial.html
source: https://carla.readthedocs.io/en/latest/python_api/#carlaboundingbox-class
"""
import os
import sys
import glob
import json
from pathlib import Path
import numpy as np

try:
    sys.path.append(glob.glob('../carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
from carla import Transform, Location  # , ColorConverter, SensorData, BoundingBox

try:
    import cv2 as cv
except ImportError:
    raise RuntimeError("Cannot import OpenCV package, please make sure it's installed")

try:
    import pygame as pyg
except ImportError:
    raise RuntimeError("Cannot import pygame package, please make sure it's installed")

# preprocessing image with carla does'nt work as well;
# importing the Image-class from carla-Library cause an RuntimeError
# because 'the class cannot be instantiated from Python'
# alternativ: use PIL-Library or OpenCV

IMG_SURFACE_WIDTH = 640
IMG_SURFACE_HEIGHT = 680
IMG_FOV = 100

BLUE_BOX_COLOR = (0, 0, 254)
RED_BOX_COLOR = (254, 32, 16)


class CustomCarlaDataset(object):
    def __init__(self):
        # self.root_dir = Path('../gui/Files/Original/')
        self.root_dir_img = Path('../res/files/rgb/')
        self.root_dir_json = Path('../res/files/json/')
        img_path = os.listdir(self.root_dir_img)
        json_path = os.listdir(self.root_dir_json)

        # self.root = os.listdir(self.root_dir)
        # Load all images and json files, sort them ensuring that they are aligned
        self.imgs = list(sorted(f for f in img_path))
        self.jsons = list(sorted(j for j in json_path))
        print('IMG and File are loaded!')
        # print(self.imgs)
        # print(self.jsons)

    def on_getting_data(self, idx):
        img = cv.imread('{}'.format(self.root_dir_img / self.imgs[idx]))
        file_content = (self.root_dir_json / self.jsons[idx]).read_text()
        json_file = json.loads(file_content, encoding='utf-8')
        print('{}'.format(self.root_dir_img / self.imgs[idx]))
        print(self.imgs[idx])
        return img, json_file, str(self.imgs[idx])

    def show(self):
        # print(self.imgs)
        # print(self.jsons)
        # tmp_img = self.root_dir / self.imgs[-1]
        # print(tmp_img)

        j_file = self.root_dir / self.jsons[-1]
        content = j_file.read_text()
        tmp_json = json.loads(content, encoding='utf-8')
        print(tmp_json['img_specs'])
        # img = Image.open(tmp_img)
        # img.frame = 429
        # img.width = tmp_json['img_specs']['width']
        # img.height = tmp_json['img_specs']['height']
        # img.fov = tmp_json['img_specs']['fov']

        print(j_file)
        print(tmp_json)
        # print(tmp_img)

        # print(img)

    def img_print(self):
        pass


#######################################################################
#               Custom class for bounding box                         #
#######################################################################

class ImageBBox(object):
    """

    """

    @staticmethod
    def on_getting_bbox(carla_actor_lst, carla_cam):
        """

        :param carla_actor_lst:
        :param carla_cam:
        :return:
        """
        bbx = [ImageBBox.on_getting_bbox(carla_actor, carla_cam) for carla_actor in carla_actor_lst]

        # add object filter -- later...
        bbx = [b for b in bbx if all(b[:, 1] > 0)]  # try to play with different values

        return bbx

    @staticmethod
    def on_drawing_bbox():
        pass


######################################################################
#                         Draw box with OpenCV                       #
######################################################################
class ObjectDetectionWithOpenCV(object):
    def __init__(self):
        print('Object detection with OpenCV : ', cv.__version__)
        pass

    @staticmethod
    def on_drawing_2(carla_img, coordinates, box_thickness=1):
        tmp_img = carla_img
        print('############################################')
        print('coord received DRAW: ', coordinates)
        print('############################################')
        for c in coordinates:
            c1 = (c[0], c[1])
            c2 = (c[2], c[3])
            print(c1)
            print(c2)
            print(c[0])
            print("C[0]: ", type(c[0]))
            tmp_img = cv.rectangle(tmp_img, c1, c2, (0, 0, 254), box_thickness)
        return tmp_img

    @staticmethod
    def _extract_bbox_coord(debug_info_dict):
        coordinate_ndarray = np.zeros((8, 4))
        print('bb ext for actor:')
        print(debug_info_dict['actor_type'])
        bbox_extent = debug_info_dict['actor_bbox_ext']
        coordinate_ndarray[0, :] = np.array([bbox_extent['x'], bbox_extent['y'], -bbox_extent['z'], 1])
        coordinate_ndarray[1, :] = np.array([-bbox_extent['x'], bbox_extent['y'], -bbox_extent['z'], 1])
        coordinate_ndarray[2, :] = np.array([-bbox_extent['x'], -bbox_extent['y'], -bbox_extent['z'], 1])
        coordinate_ndarray[3, :] = np.array([bbox_extent['x'], -bbox_extent['y'], -bbox_extent['z'], 1])
        coordinate_ndarray[4, :] = np.array([bbox_extent['x'], bbox_extent['y'], bbox_extent['z'], 1])
        coordinate_ndarray[5, :] = np.array([-bbox_extent['x'], bbox_extent['y'], bbox_extent['z'], 1])
        coordinate_ndarray[6, :] = np.array([-bbox_extent['x'], -bbox_extent['y'], bbox_extent['z'], 1])
        coordinate_ndarray[7, :] = np.array([bbox_extent['x'], bbox_extent['y'], bbox_extent['z'], 1])

        return coordinate_ndarray

    @staticmethod
    def filter_bbox_to_draw(debug_info_dict, carla_cam, calibration):
        actor_bbx_coord = ObjectDetectionWithOpenCV._extract_bbox_coord(debug_info_dict)
        xyz_coord = ObjectDetectionWithOpenCV._actor_info_from_sensor_to_coord(actor_bbx_coord, debug_info_dict,
                                                                               carla_cam)[
                    :3, :]
        box_coord = np.concatenate([xyz_coord[1, :], -xyz_coord[2, :], xyz_coord[0, :]])
        bbx = np.transpose(np.dot(calibration, box_coord))
        cam_bbx = np.concatenate([bbx[:, 0] / bbx[:, 2], bbx[:, 1] / bbx[:, 2], bbx[:, 2]], axis=1)

        return cam_bbx

    @staticmethod
    def on_getting_bbox(carla_actor_lst, carla_cam, calibration):
        """

        :param carla_actor_lst:
        :param carla_cam:
        :return:
        """
        bbx = [ObjectDetectionWithOpenCV.filter_bbox_to_draw(carla_actor, carla_cam, calibration) for carla_actor in
               carla_actor_lst]
        print("BBX (before): ", len(bbx))
        # add object filter -- later...
        bbx = [b for b in bbx if all(b[:, 2] > 0)]  # try to play with different values
        print("len BBX (after): ", len(bbx))
        return bbx

    @staticmethod
    def on_displaying_img(carla_img):
        cv.imshow("IMG", carla_img)
        cv.waitKey(0)
        cv.destroyWindow('IMG')
        return

    @staticmethod
    def on_saving_img(carla_img, new_img_name):
        cv.imwrite(new_img_name, carla_img)
        return

    @staticmethod
    def convert_actor_info_to_numpy(actor_info_dict):
        """

        :param actor_info_dict:
        :return:
        """
        roll = actor_info_dict['actor_rotation']['roll']
        pitch = actor_info_dict['actor_rotation']['pitch']
        yaw = actor_info_dict['actor_rotation']['yaw']

        rot_mat = np.matrix(np.identity(4))

        # find the angle of the rotation in (z, y, x) in radians
        cos_yaw = np.cos(np.radians(yaw))
        cos_pitch = np.cos(np.radians(pitch))
        cos_roll = np.cos(np.radians(roll))
        sin_yaw = np.sin(np.radians(yaw))
        sin_pitch = np.sin(np.radians(pitch))
        sin_roll = np.sin(np.radians(roll))

        rot_mat[0, 0] = cos_yaw * cos_pitch
        rot_mat[0, 1] = cos_yaw * sin_pitch * sin_roll - sin_yaw * cos_roll
        rot_mat[0, 2] = cos_yaw * sin_pitch * cos_roll + cos_yaw * sin_roll

        rot_mat[1, 0] = sin_yaw * cos_pitch
        rot_mat[1, 1] = sin_yaw * sin_pitch * sin_roll + cos_yaw * cos_roll
        rot_mat[1, 2] = sin_yaw * sin_pitch * cos_roll - cos_yaw * sin_roll

        rot_mat[2, 0] = -sin_pitch
        rot_mat[2, 1] = cos_pitch * sin_roll
        rot_mat[2, 2] = cos_pitch * cos_roll

        rot_mat[0, 3] = actor_info_dict['actor_location']['x']
        rot_mat[1, 3] = actor_info_dict['actor_location']['y']
        rot_mat[2, 3] = actor_info_dict['actor_location']['z']

        return rot_mat

    @staticmethod
    def convert_cam_info_to_numpy(camera_info):
        """
        This method take information about the camera sensor saves in a json file
        :param camera_info:
        :return:
        """
        roll = camera_info['cam_rotation']['roll']
        pitch = camera_info['cam_rotation']['pitch']
        yaw = camera_info['cam_rotation']['yaw']
        rot_mat = np.identity(4)

        # find the angle of the rotation in (z, y, x) in radians
        cos_yaw = np.cos(np.radians(yaw))
        cos_pitch = np.cos(np.radians(pitch))
        cos_roll = np.cos(np.radians(roll))
        sin_yaw = np.sin(np.radians(yaw))
        sin_pitch = np.sin(np.radians(pitch))
        sin_roll = np.sin(np.radians(roll))

        rot_mat[0, 0] = cos_yaw * cos_pitch
        rot_mat[0, 1] = cos_yaw * sin_pitch * sin_roll - sin_yaw * cos_roll
        rot_mat[0, 2] = cos_yaw * sin_pitch * cos_roll + cos_yaw * sin_roll

        rot_mat[1, 0] = sin_yaw * cos_pitch
        rot_mat[1, 1] = sin_yaw * sin_pitch * sin_roll + cos_yaw * cos_roll
        rot_mat[1, 2] = sin_yaw * sin_pitch * cos_roll - cos_yaw * sin_roll

        rot_mat[2, 0] = -sin_pitch
        rot_mat[2, 1] = cos_pitch * sin_roll
        rot_mat[2, 2] = cos_pitch * cos_roll

        rot_mat[0, 3] = camera_info['cam_location']['x']
        rot_mat[1, 3] = camera_info['cam_location']['y']
        rot_mat[2, 3] = camera_info['cam_location']['z']
        return rot_mat

    @staticmethod
    def _convert_sensor_info_to_numpy(bbox_coord, sensor_data_dict):
        sensor_matrix = ObjectDetectionWithOpenCV.convert_cam_info_to_numpy(sensor_data_dict)
        inv_sensor_matrix = np.linalg.inv(sensor_matrix)
        coord_to_numpy = np.dot(inv_sensor_matrix, bbox_coord)

        return coord_to_numpy

    @staticmethod
    def _convert_actor_info_to_numpy(bb_coord, actor_info_dict):
        actor_transform = ObjectDetectionWithOpenCV.convert_actor_info_to_numpy(actor_info_dict)
        actor_coord_array = np.dot(actor_transform, np.transpose(bb_coord))
        return actor_coord_array

    @staticmethod
    def _actor_info_from_sensor_to_coord(bbox_coord, actor_info_dict, sensor_data_dict):
        actor_coord_np = ObjectDetectionWithOpenCV._convert_actor_info_to_numpy(bbox_coord, actor_info_dict)
        sensor_coord_np = ObjectDetectionWithOpenCV._convert_sensor_info_to_numpy(actor_coord_np,
                                                                                  sensor_data_dict)
        # print("Sensor coord shape: ", sensor_coord_np.shape)
        return sensor_coord_np

    @staticmethod
    def on_calibrate(img_width, img_height, img_fov):
        calibration = np.identity(3)
        calibration[0, 0] = img_width / (2. * np.tan(img_fov * np.pi / 360.0))
        calibration[0, 2] = img_width / 2.0
        calibration[1, 1] = calibration[0, 0]
        calibration[1, 2] = img_height / 2.0
        return calibration

    @staticmethod
    def extract_2d_coordinate(bbox):
        coordinates = []
        print('method pygame 2D ')
        print('LEN BBX: ', len(bbox))
        inc = 0
        print('starting increment bbx iteration: ', inc)
        for b in bbox:
            inc += 1
            print("--------------- {} ------------".format(inc))
            point2d = [(int(b[i, 0]), int(b[i, 1])) for i in range(8)]
            xmin = point2d[0][0]
            ymin = point2d[0][1]
            xmax = point2d[0][0]
            ymax = point2d[0][1]
            # print("type of point: ", type(point2d), 'type of minx: ', type(xmin))
            print('Len point2d: ', len(point2d))
            # print(xmin)
            for p in point2d:
                if xmin >= 0:
                    if p[0] >= 0 and p[0] <= xmin:
                        xmin = p[0]
                else:
                    if p[0] >= 0:
                        xmin = p[0]
                if p[0] >= 0 and p[0] >= xmax:
                    xmax = p[0]
                if p[1] <= ymin:
                    ymin = p[1]
                if p[1] >= ymax:
                    ymax = p[1]
            if xmin < 0 or xmin == xmax:
                print('unable to get values to draw box : ', xmin, xmax, ymin, ymax)
            else:
                print('value got ~(^v^)~')
                p0 = (xmin, ymin)
                # p1 = (xmin, ymax)
                p2 = (xmax, ymax)
                # p4 = (xmax, ymin)
                if ((xmax - xmin) >= 10) and ((ymax - ymin) >= 20):
                    coordinates.append(p0 + p2)
                    print('Vehicle added [- -]')
                # else:
                #    print('too far from the scene (vehicle): ', xmin, xmax, ymin, ymax)
                elif ((xmax - xmin) >= 10) and ((ymax - ymin) >= 10):
                    coordinates.append(p0 + p2)
                    print('pedestrian added (° °)')
                else:
                    print('too far from the scene: ', xmin, xmax, ymin, ymax)
        print('++++++++++++++++++++++++ COORD IN POINT 2D ++++++++++++++++++')
        print(coordinates)
        print('++++++++++++++++++++++END ++++++++++++++++++++++++++++++++++')
        return coordinates

    @staticmethod
    def draw_2d_box(coordinates, im, im_name):
        path_im = os.path.join('/home/rack/', '{}_modified.png'.format(im))
        print("IMA: ")

        imm = ObjectDetectionWithOpenCV.on_drawing_2(im, coordinates)
        cv.imshow("{}".format(im_name), im)
        cv.imwrite(path_im, imm)
        cv.waitKey(0)
        cv.destroyWindow("{}".format(im_name))

    @staticmethod
    def play():
        try:
            dataset = CustomCarlaDataset()
            im, jfile, im_name = dataset.on_getting_data(10)
            debug_info = jfile['debug_info'][0]
            rot_matrix = ObjectDetectionWithOpenCV.convert_actor_info_to_numpy(debug_info)
            calib = ObjectDetectionWithOpenCV.on_calibrate(jfile['img_width'], jfile['img_height'], jfile['img_fov'])
            cam_inf = ObjectDetectionWithOpenCV.convert_cam_info_to_numpy(jfile)

            cbbx = ObjectDetectionWithOpenCV.filter_bbox_to_draw(debug_info, jfile, calib)
            info = jfile['debug_info']
            info_bmw = []
            info_bmw.append(info[14])
            gbox = ObjectDetectionWithOpenCV.on_getting_bbox(info, jfile, calib)

            pyboxcoord = ObjectDetectionWithOpenCV.extract_2d_coordinate(gbox)
            print('############# PYBOX #################')
            print(pyboxcoord)
            print('++++++++++ THE END +++++++++++')
            ObjectDetectionWithOpenCV.draw_2d_box(pyboxcoord, im, im_name)
        finally:
            # pyg.quit()
            print('Ciao Pygame!')


if __name__ == '__main__':
    ObjectDetectionWithOpenCV.play()
