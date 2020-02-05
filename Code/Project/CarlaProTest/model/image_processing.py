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

try:
    import cv2 as cv
except ImportError:
    raise RuntimeError("Cannot import OpenCV package, please make sure it's installed")

# preprocessing image with carla does'nt work as well;
# importing the Image-class from carla-Library cause an RuntimeError
# because 'the class cannot be instantiated from Python'
# alternativ: use PIL-Library or OpenCV

BLUE_BOX_COLOR = (254, 0, 0)
RED_BOX_COLOR = (16, 32, 254)


#####################################################################
#          Custom class to read saved images and json files         #
#####################################################################

class CustomCarlaDataset(object):
    root_dir_img = Path('../res/files/rgb/')
    root_dir_json = Path('../res/files/json/')
    # root_dir_copy = None
    IMG_LST = None
    JSON_LST = None

    def __init__(self):
        print('path set')

    @staticmethod
    def _load_dataset():
        # CustomCarlaDataset.root_dir_json = Path('../res/files/copy/')
        img_path = os.listdir(CustomCarlaDataset.root_dir_img)
        json_path = os.listdir(CustomCarlaDataset.root_dir_json)

        # Load all images and json files, sort them ensuring that they are aligned
        imgs = list(sorted(f for f in img_path))
        jsons = list(sorted(j for j in json_path))
        print('IMG and File are loaded!')
        return imgs, jsons

    @staticmethod
    def load():
        CustomCarlaDataset.IMG_LST, CustomCarlaDataset.JSON_LST = CustomCarlaDataset._load_dataset()
        # print(CustomCarlaDataset.IMG_LST[0])
        return CustomCarlaDataset.IMG_LST, CustomCarlaDataset.JSON_LST

    @staticmethod
    def on_load_img(idx):
        print('load img...')
        img = cv.imread('{}'.format(CustomCarlaDataset.root_dir_img / CustomCarlaDataset.IMG_LST[idx]))
        # print(type(img))
        return img, str(CustomCarlaDataset.IMG_LST[idx])

    @staticmethod
    def on_load_file(idx):
        file_content = (CustomCarlaDataset.root_dir_json / CustomCarlaDataset.JSON_LST[idx]).read_text()
        json_file = json.loads(file_content, encoding='utf-8')
        return json_file

    @staticmethod
    def rearrang_img_for_gui(arr_img):
        """
        OpenCV read Image color in Blue, Green, Red; the color priority must be rearrange
        (split) before display it with oder Image-library as PIL or ImageTK
        """
        print('re-arrange image...')
        blue, green, red = cv.split(arr_img)
        rearranged_img = cv.merge((red, green, blue))
        return rearranged_img


#######################################################################
#               Custom class for bounding box                         #
#######################################################################

class ImageBBoxCoordinate(object):
    """
    Class to calculate object coordinates in and image through object's information
    saved in a json file
    """

    @staticmethod
    def extract_actor_info_from_dict(actor_info_dict):
        """
        take extracted information about an actor from the json file as dictionary and
        return a matrix containing the angle it 3D rotation according to (yaw, pitch, roll)
        reference: http://planning.cs.uiuc.edu/node102.html

        rot_mat (yaw, pitch, roll) = R_z(yaw) x R_y(pitch) x R_x(roll)

        :param actor_info_dict:
        :return: rot_mat
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
    def extract_camera_info_from_dict(camera_info):
        """
        Extract the camera's information from the json file
        (for more info see method: "extract_actor_info_from_dict(...)"
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
    def _convert_camera_info_to_numpy(bbox_coord, sensor_data_dict):
        camera_matrix = ImageBBoxCoordinate.extract_camera_info_from_dict(sensor_data_dict)
        inv_camera_matrix = np.linalg.inv(camera_matrix)
        coord_to_numpy = np.dot(inv_camera_matrix, bbox_coord)

        return coord_to_numpy

    @staticmethod
    def _convert_actor_info_to_numpy(bb_coord, actor_info_dict):
        actor_transform = ImageBBoxCoordinate.extract_actor_info_from_dict(actor_info_dict)
        actor_coord_array = np.dot(actor_transform, np.transpose(bb_coord))
        return actor_coord_array

    @staticmethod
    def _actor_coordinate_from_camera(bbox_coord, actor_info_dict, sensor_data_dict):
        actor_coord_np = ImageBBoxCoordinate._convert_actor_info_to_numpy(bbox_coord, actor_info_dict)
        sensor_coord_np = ImageBBoxCoordinate._convert_camera_info_to_numpy(actor_coord_np,
                                                                            sensor_data_dict)

        return sensor_coord_np

    @staticmethod
    def on_calibrate(img_width, img_height, img_fov):
        """
        return back the calibration matrix according the formula:
                      | f(x)  0    c_x |
        calibration = |   0  f(y)  c_y |
                      |   0   0     1  |
        reference:
        https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html#calibration
        :param img_width:
        :param img_height:
        :param img_fov:
        :return: calibration
        """
        calibration = np.identity(3)
        calibration[0, 0] = img_width / (2. * np.tan(img_fov * np.pi / 360.0))
        calibration[0, 2] = img_width / 2.0
        calibration[1, 1] = calibration[0, 0]
        calibration[1, 2] = img_height / 2.0
        print("Calibration angle: ", calibration[0, 0])
        return calibration

    @staticmethod
    def extract_2d_coordinate(bbox, actor_type, actor_id):
        coordinates = []
        typ_text = []
        id_text = []
        print('method pygame 2D ')
        inc = 0
        print('starting increment bbx iteration: ', inc)
        for b, a_typ, a_id in zip(bbox, actor_type, actor_id):
            inc += 1
            print("--------------- {} ------------".format(inc))
            point2d = [(int(b[i, 0]), int(b[i, 1])) for i in range(8)]
            xmin = point2d[0][0]
            ymin = point2d[0][1]
            xmax = point2d[0][0]
            ymax = point2d[0][1]

            # print('Len point2d: ', len(point2d))
            for p in point2d:
                if xmin >= 0:
                    if 0 <= p[0] <= xmin:
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
                print('unable to get values to draw box : ', xmin, xmax, ymin, ymax, ' for actor: ', a_typ, 'with ID: ', a_id)
                # print('actor: ', a, ' piouff')
            else:
                print('value got ~(^v^)~')
                p0 = (xmin, ymin)
                p2 = (xmax, ymax)

                if ((xmax - xmin) >= 10) and ((ymax - ymin) >= 20):
                    coordinates.append(p0 + p2)
                    typ_text.append(a_typ)
                    id_text.append(a_id)
                    print('Vehicle added [- -]: --> TYP: ', a_typ, ' ID: ', a_id)
                elif ((xmax - xmin) >= 10) and ((ymax - ymin) >= 10):
                    coordinates.append(p0 + p2)
                    typ_text.append(a_typ)
                    id_text.append(a_id)
                    print('pedestrian added (° °): --> TYP: ', a_typ, ' ID: ', a_id)
                else:
                    print('too far from the scene: ', xmin, xmax, ymin, ymax)
        # print('++++++++++++++++++++++++ COORD IN POINT 2D ++++++++++++++++++')
        # print(coordinates)
        # print(id_text)
        print('++++++++++++++++++++++END ++++++++++++++++++++++++++++++++++')
        return coordinates, typ_text, id_text

    @staticmethod
    def _extract_bbox_coord(debug_info_dict):
        coordinate_ndarray = np.zeros((8, 4))
        actor_type = debug_info_dict['actor_type']
        actor_id = debug_info_dict['actor_id']
        # print('bb ext for actor:')
        # print(debug_info_dict['actor_type'])
        bbox_extent = debug_info_dict['actor_bbox_ext']
        coordinate_ndarray[0, :] = np.array([bbox_extent['x'], bbox_extent['y'], -bbox_extent['z'], 1])
        coordinate_ndarray[1, :] = np.array([-bbox_extent['x'], bbox_extent['y'], -bbox_extent['z'], 1])
        coordinate_ndarray[2, :] = np.array([-bbox_extent['x'], -bbox_extent['y'], -bbox_extent['z'], 1])
        coordinate_ndarray[3, :] = np.array([bbox_extent['x'], -bbox_extent['y'], -bbox_extent['z'], 1])
        coordinate_ndarray[4, :] = np.array([bbox_extent['x'], bbox_extent['y'], bbox_extent['z'], 1])
        coordinate_ndarray[5, :] = np.array([-bbox_extent['x'], bbox_extent['y'], bbox_extent['z'], 1])
        coordinate_ndarray[6, :] = np.array([-bbox_extent['x'], -bbox_extent['y'], bbox_extent['z'], 1])
        coordinate_ndarray[7, :] = np.array([bbox_extent['x'], bbox_extent['y'], bbox_extent['z'], 1])

        return coordinate_ndarray, actor_type, actor_id

    @staticmethod
    def filter_bbox_to_draw(debug_info_dict, carla_cam, calibration):
        actor_bbx_coord, actor_type, actor_id = ImageBBoxCoordinate._extract_bbox_coord(debug_info_dict)
        xyz_coord = ImageBBoxCoordinate._actor_coordinate_from_camera(actor_bbx_coord, debug_info_dict,
                                                                      carla_cam)[
                    :3, :]
        box_coord = np.concatenate([xyz_coord[1, :], -xyz_coord[2, :], xyz_coord[0, :]])
        bbx = np.transpose(np.dot(calibration, box_coord))
        cam_bbx = np.concatenate([bbx[:, 0] / bbx[:, 2], bbx[:, 1] / bbx[:, 2], bbx[:, 2]], axis=1)

        return cam_bbx, actor_type, actor_id

    @staticmethod
    def on_getting_bbox(carla_actor_lst, carla_cam, calibration):
        """
        take information of all actors and that for the camera, then use the calcuted
        calibration to give the coordinates of the window to draw that contain the
        object.

        :param calibration:
        :param carla_actor_lst:
        :param carla_cam:
        :return:
        """
        bbx = []
        actor_type = []
        actor_id = []
        for carla_actor in carla_actor_lst:
            bb, act_typ, act_id = ImageBBoxCoordinate.filter_bbox_to_draw(carla_actor, carla_cam, calibration)
            bbx.append(bb)
            actor_type.append(act_typ)
            actor_id.append(act_id)
        # bbx = [ImageBBoxCoordinate.filter_bbox_to_draw(carla_actor, carla_cam, calibration) for carla_actor in
        #        carla_actor_lst]
        # print("BBX (before): ", len(bbx))
        # print("len TYP: ", len(actor_type))
        # add object filter -- later...

        actor_type_ = []
        actor_id_ = []
        bbx_ = []
        for box, typ, _id in zip(bbx, actor_type, actor_id):
            if all(box[:, 2] > 0):
                bbx_.append(box)
                actor_type_.append(typ)
                actor_id_.append(_id)
                # print('type appended: ', typ)

        bbx = bbx_
        actor_type = actor_type_
        actor_id = actor_id_

        bbx = [b for b in bbx if all(b[:, 2] > 0)]  # try to play with different values
        # print("len BBX (after): ", len(bbx))
        # print("len TYP (after): ", len(actor_type))
        return bbx, actor_type, actor_id


######################################################################
#                         Draw box with OpenCV                       #
######################################################################
class ObjectDetectionWithOpenCV(object):
    path_img_copy = Path('../res/files/copy/')

    def __init__(self):
        print('Object detection with OpenCV : ', cv.__version__)
        pass

    @staticmethod
    def on_drawing_2d_box(carla_img, coordinates, actor_type, actor_id, box_thickness=1):
        tmp_img = carla_img
        # print('############################################')
        # print('coord received DRAW: ', coordinates)
        # print('############################################')
        for c, a, i in zip(coordinates, actor_type, actor_id):
            c1 = (c[0], c[1])
            c2 = (c[2], c[3])
            c3 = (c[0], c[1]-10)
            # print(c1)
            # print(c2)
            # print(c[0])
            # print("C[0]: ", type(c[0]))
            # print('type (a): ', type(a), ' a: ', a)

            tmp_img = cv.rectangle(tmp_img, c1, c2, (0, 0, 254), box_thickness)
            cv.putText(tmp_img, "ID: "+str(i), c3, cv.FONT_HERSHEY_PLAIN, 0.8, (255, 255, 255), box_thickness)
        return tmp_img

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
    def on_saving_copy(img, img_name):
        path = Path('../res/files/copy')
        img_n = path / 'copy-{}'.format(img_name)
        print(img_n)
        cv.imwrite(str(img_n), img)
        print('Image saved!')

    @staticmethod
    def draw_2d_box(coordinates, im, actor_typs, actor_ids):
        path_im = os.path.join('/home/rack/', '{}_modified.png'.format(im))
        print("IMA: ")

        imm = ObjectDetectionWithOpenCV.on_drawing_2d_box(im, coordinates, actor_typs, actor_ids)
        # print("type im  imshow: ", type(im))
        # print("type imm  imshow: ", type(imm))
        # cv.imshow("{}".format(im_name), im)
        # cv.imwrite(path_im, imm)
        # cv.waitKey(0)
        # ObjectDetectionWithOpenCV.on_saving_copy(imm, im_name)
        # cv.destroyWindow("{}".format(im_name))
        return imm

    @staticmethod
    def on_draw(image, json_file):
        print('starting image processing...')
        calibrate = ImageBBoxCoordinate.on_calibrate(json_file['img_width'], json_file['img_height'], json_file['img_fov'])
        coord, obj_typ, obj_id = ImageBBoxCoordinate.on_getting_bbox(json_file['debug_info'], json_file, calibrate)
        box_coor, label_typ, label_id = ImageBBoxCoordinate.extract_2d_coordinate(coord, obj_typ, obj_id)
        box_img = ObjectDetectionWithOpenCV.draw_2d_box(box_coor, image, label_typ, label_id)
        print('type: ', type(box_img))
        return box_img

    @staticmethod
    def play():
        try:
            img_lst, json_lst = CustomCarlaDataset.load()
            im, im_name = CustomCarlaDataset.on_load_img(3)
            jfile = CustomCarlaDataset.on_load_file(3)
            # debug_info = jfile['debug_info'][0]
            # calib = ImageBBoxCoordinate.on_calibrate(jfile['img_width'], jfile['img_height'], jfile['img_fov'])
            #
            # info = jfile['debug_info']
            # gbox, a_typ, a_id = ImageBBoxCoordinate.on_getting_bbox(info, jfile, calib)
            #
            # pyboxcoord, typ_text, id_text = ImageBBoxCoordinate.extract_2d_coordinate(gbox, a_typ, a_id)
            # print('############# PYBOX #################')
            # print(pyboxcoord)
            # print('++++++++++ THE END +++++++++++')
            # ObjectDetectionWithOpenCV.draw_2d_box(pyboxcoord, im, typ_text, id_text)
            img = ObjectDetectionWithOpenCV.on_draw(im, jfile)
        finally:
            # pyg.quit()
            print('Ciao !')


if __name__ == '__main__':
    ObjectDetectionWithOpenCV.play()
