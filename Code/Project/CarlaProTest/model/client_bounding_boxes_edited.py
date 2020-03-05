#!/usr/bin/env python

# Copyright (c) 2019 Aptiv
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.
# modified by Ruphus, Feb 24, 2020 19:00

"""
An example of client-side bounding boxes with basic car controls.

Controls:

    W            : throttle
    S            : brake
    AD           : steer
    Space        : hand-brake

    ESC          : quit
"""

# ==============================================================================
# -- find carla module ---------------------------------------------------------
# ==============================================================================


import glob
import os
import sys
from pathlib import Path

try:
    sys.path.append(glob.glob('../carla/CARLA_0.9.6/PythonAPI/carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# ==============================================================================
# -- imports -------------------------------------------------------------------
# ==============================================================================

import carla

import weakref
import random
from PIL import Image
import cv2 as cv
import json

try:
    import pygame
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_SPACE
    from pygame.locals import K_q
    from pygame.locals import K_d
    from pygame.locals import K_s
    from pygame.locals import K_z
    from pygame.locals import K_f
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

VIEW_WIDTH = 1920 // 2
VIEW_HEIGHT = 1080 // 2
VIEW_FOV = 90

BB_COLOR = (248, 64, 24)


# ==============================================================================
# -- ClientSideBoundingBoxes ---------------------------------------------------
# ==============================================================================

class Draw_Box_On_Image:

    def __init__(self):
        print("Start ")

    @staticmethod
    def draw_box_1(_img, points, color):
        new_image = _img

        for point in points:
            p1 = (point[0], point[1])
            p2 = (point[2], point[3])
            border = 1
            print('P1: ', p1)
            print('P2": ', p2)
            print(type(new_image))
            new_image = cv.rectangle(new_image, p1, p2, color, border)

        return new_image


class ClientSideBoundingBoxes(object):
    """
    This is a module responsible for creating 2D bounding boxes and drawing them
    client-side on pygame surface.
    """

    @staticmethod
    def get_bounding_boxes(v_objects, p_objects, camera):
        """
        Creates 3D bounding boxes based on carla actors list and camera.
        """

        v_bounding_boxes = []
        v_objects_ids = []

        p_bounding_boxes = []
        p_objects_ids = []

        for v_object in v_objects:
            v_bbox, v_id = ClientSideBoundingBoxes.get_bounding_box(v_object, camera)
            v_bounding_boxes.append(v_bbox)
            v_objects_ids.append(v_id)

        for p_object in p_objects:
            p_bbox, p_id = ClientSideBoundingBoxes.get_bounding_box(p_object, camera)
            p_bounding_boxes.append(p_bbox)
            p_objects_ids.append(p_id)

        # filter objects behind camera
        v_filter_bbx = []
        v_filter_id = []
        for v_box, v_id in zip(v_bounding_boxes, v_objects_ids):
            if all(v_box[:, 2] > 0):
                v_filter_bbx.append(v_box)
                v_filter_id.append(v_id)

        p_filter_bbx = []
        p_filter_id = []
        for p_box, p_id in zip(p_bounding_boxes, p_objects_ids):
            if all(p_box[:, 2] > 0):
                p_filter_bbx.append(p_box)
                p_filter_id.append(p_id)

        p_bounding_boxes = p_filter_bbx
        p_objects_ids = p_filter_id
        print("BOX SIZE: {} ID SIZE: {}".format(len(v_bounding_boxes), len(v_objects_ids)))

        return v_bounding_boxes, v_objects_ids, p_bounding_boxes, p_objects_ids

    @staticmethod
    def get_coords_boxes(display, v_bounding_boxes, v_actor_ids, p_bounding_boxes, p_actor_ids):
        """
        get Coordinate without to draw bounding boxes on pygame display.
        """
        v_opencv_box_coords = []
        v_id_box = []

        p_opencv_box_coords = []
        p_id_box = []

        bb_surface = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
        bb_surface.set_colorkey((0, 0, 0))

        # vehicles
        for v_bbox, v_id in zip(v_bounding_boxes, v_actor_ids):
            points = [(int(v_bbox[i, 0]), int(v_bbox[i, 1])) for i in range(8)]

            print(points)
            min_x = points[0][0]
            min_y = points[0][1]
            max_x = points[0][0]
            max_y = points[0][1]
            for point in points:
                if min_x >= 0:
                    if point[0] >= 0 and point[0] <= min_x:
                        min_x = point[0]
                else:
                    if point[0] >= 0:
                        min_x = point[0]

                if point[0] >= 0 and point[0] >= max_x:
                    max_x = point[0]

                if point[1] <= min_y:
                    min_y = point[1]
                if point[1] >= max_y:
                    max_y = point[1]
            if min_x < 0 or min_x == max_x:
                print("unable to find extrema values:", min_x, max_x, min_y, max_y)
            else:
                print("rectangle points:", min_x, max_x, min_y, max_y, "   id: ", v_id)
                point1 = (min_x, min_y)  # top left
                point2 = (min_x, max_y)  # bottom left
                point3 = (max_x, max_y)  # bottom right
                point4 = (max_x, min_y)  # top right
                v_opencv_box_coords.append((point1 + point3))
                v_id_box.append(v_id)

        # pedestrians
        for p_bbox, p_id in zip(p_bounding_boxes, p_actor_ids):
            points = [(int(p_bbox[i, 0]), int(p_bbox[i, 1])) for i in range(8)]

            print(points)
            min_x = points[0][0]
            min_y = points[0][1]
            max_x = points[0][0]
            max_y = points[0][1]
            for point in points:
                if min_x >= 0:
                    if point[0] >= 0 and point[0] <= min_x:
                        min_x = point[0]
                else:
                    if point[0] >= 0:
                        min_x = point[0]

                if point[0] >= 0 and point[0] >= max_x:
                    max_x = point[0]

                if point[1] <= min_y:
                    min_y = point[1]
                if point[1] >= max_y:
                    max_y = point[1]
            if min_x < 0 or min_x == max_x:
                print("unable to find extrema values:", min_x, max_x, min_y, max_y)
            else:
                print("rectangle points:", min_x, max_x, min_y, max_y, "   id: ", p_id)
                point1 = (min_x, min_y)  # top left
                point2 = (min_x, max_y)  # bottom left
                point3 = (max_x, max_y)  # bottom right
                point4 = (max_x, min_y)  # top right

                p_opencv_box_coords.append((point1 + point3))
                p_id_box.append(p_id)
        display.blit(bb_surface, (0, 0))
        return v_opencv_box_coords, v_id_box, p_opencv_box_coords, p_id_box

    @staticmethod
    def get_bounding_box(_object, camera):
        """
        Returns 3D bounding box for an _object based on camera view.
        """

        bb_cords = ClientSideBoundingBoxes._create_bb_points(_object)
        cords_x_y_z = ClientSideBoundingBoxes._object_to_sensor(bb_cords, _object, camera)[:3, :]
        cords_y_minus_z_x = np.concatenate([cords_x_y_z[1, :], -cords_x_y_z[2, :], cords_x_y_z[0, :]])
        bbox = np.transpose(np.dot(camera.calibration, cords_y_minus_z_x))
        camera_bbox = np.concatenate([bbox[:, 0] / bbox[:, 2], bbox[:, 1] / bbox[:, 2], bbox[:, 2]], axis=1)
        return camera_bbox, _object.id

    @staticmethod
    def _create_bb_points(_object):
        """
        Returns 3D bounding box for an _object.
        """

        cords = np.zeros((8, 4))
        extent = _object.bounding_box.extent
        cords[0, :] = np.array([extent.x, extent.y, -extent.z, 1])
        cords[1, :] = np.array([-extent.x, extent.y, -extent.z, 1])
        cords[2, :] = np.array([-extent.x, -extent.y, -extent.z, 1])
        cords[3, :] = np.array([extent.x, -extent.y, -extent.z, 1])
        cords[4, :] = np.array([extent.x, extent.y, extent.z, 1])
        cords[5, :] = np.array([-extent.x, extent.y, extent.z, 1])
        cords[6, :] = np.array([-extent.x, -extent.y, extent.z, 1])
        cords[7, :] = np.array([extent.x, -extent.y, extent.z, 1])
        return cords

    @staticmethod
    def _object_to_sensor(cords, _object, sensor):
        """
        Transforms coordinates of an _object bounding box to sensor.
        """

        world_cord = ClientSideBoundingBoxes._object_to_world(cords, _object)
        sensor_cord = ClientSideBoundingBoxes._world_to_sensor(world_cord, sensor)
        return sensor_cord

    @staticmethod
    def _object_to_world(cords, _object):
        """
        Transforms coordinates of an _object bounding box to world.
        """

        bb_transform = carla.Transform(_object.bounding_box.location)
        bb_object_matrix = ClientSideBoundingBoxes.get_matrix(bb_transform)
        object_world_matrix = ClientSideBoundingBoxes.get_matrix(_object.get_transform())
        bb_world_matrix = np.dot(object_world_matrix, bb_object_matrix)
        world_cords = np.dot(bb_world_matrix, np.transpose(cords))
        return world_cords

    @staticmethod
    def _world_to_sensor(cords, sensor):
        """
        Transforms world coordinates to sensor.
        """

        sensor_world_matrix = ClientSideBoundingBoxes.get_matrix(sensor.get_transform())
        world_sensor_matrix = np.linalg.inv(sensor_world_matrix)
        sensor_cords = np.dot(world_sensor_matrix, cords)
        return sensor_cords

    @staticmethod
    def get_matrix(transform):
        """
        Creates matrix from carla transform.
        """

        rotation = transform.rotation
        location = transform.location
        c_y = np.cos(np.radians(rotation.yaw))
        s_y = np.sin(np.radians(rotation.yaw))
        c_r = np.cos(np.radians(rotation.roll))
        s_r = np.sin(np.radians(rotation.roll))
        c_p = np.cos(np.radians(rotation.pitch))
        s_p = np.sin(np.radians(rotation.pitch))
        matrix = np.matrix(np.identity(4))
        matrix[0, 3] = location.x
        matrix[1, 3] = location.y
        matrix[2, 3] = location.z
        matrix[0, 0] = c_p * c_y
        matrix[0, 1] = c_y * s_p * s_r - s_y * c_r
        matrix[0, 2] = -c_y * s_p * c_r - s_y * s_r
        matrix[1, 0] = s_y * c_p
        matrix[1, 1] = s_y * s_p * s_r + c_y * c_r
        matrix[1, 2] = -s_y * s_p * c_r + c_y * s_r
        matrix[2, 0] = s_p
        matrix[2, 1] = -c_p * s_r
        matrix[2, 2] = c_p * c_r
        return matrix


# ==============================================================================
# -- BasicSynchronousClient ----------------------------------------------------
# ==============================================================================


class BasicSynchronousClient(object):
    """
    Basic implementation of a synchronous client.
    """

    def __init__(self):
        self.client = None
        self.world = None
        self.camera = None

        self.vehicles = None
        self.pedestrians = None
        self.ai_controllers = None

        self.display = None
        self.image = None
        self.capture = True
        self.image_name = None

        self.original_img_path = Path('../res/img/originals')
        self.edited_img_path = Path('../res/img/edited')
        self.jsons_path = Path('../res/img/jsons')

        self.custom_annotation = {
            'image_name': '',
            'object_1': {
                'class': 'vehicle',
                'identify': []
            },
            'object_2': {
                'class': 'pedestrian',
                'identify': []
            }
        }

    def camera_blueprint(self):
        """
        Returns camera blueprint.
        """

        camera_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(VIEW_WIDTH))
        camera_bp.set_attribute('image_size_y', str(VIEW_HEIGHT))
        camera_bp.set_attribute('fov', str(VIEW_FOV))
        return camera_bp

    def set_synchronous_mode(self, synchronous_mode):
        """
        Sets synchronous mode.
        """

        settings = self.world.get_settings()
        settings.synchronous_mode = synchronous_mode
        self.world.apply_settings(settings)

    def create_and_spawn_vehicles(self, number_of_vehicles=20):
        """
        Spawn vehicles in the world, set all vehicle to self-drive mode
        """
        print("Adding vehicles...")
        self.vehicles = []
        # spawns vehicle and get the first one to attach a camera on it
        vehicles_bp = self.world.get_blueprint_library().filter('vehicle.*')
        car_bp = vehicles_bp[0]

        spawn_points = self.world.get_map().get_spawn_points()

        for i, transform in enumerate(spawn_points):
            if i == 0:
                test_car = self.world.spawn_actor(car_bp, transform)
                test_car.set_autopilot()
                self.vehicles.append(test_car)
            elif i >= number_of_vehicles:
                break
            else:
                vehicle_bp = random.choice(vehicles_bp)
                vehicle = self.world.spawn_actor(vehicle_bp, transform)
                vehicle.set_autopilot()
                self.vehicles.append(vehicle)
        print("number of vehicles added: ", len(self.vehicles))
        # location = random.choice(self.world.get_map().get_spawn_points())

    def create_and_spawn_pedestrians(self, number_of_pedestrians=40):
        """
        spawn walker in the world
        """
        print("Adding pedestrians...")
        # create a list to put all walkers together. so we could remove them from the world
        self.pedestrians = []
        self.ai_controllers = []
        pedestrians_ids = []

        # load the walker library and it controller library
        pedestrians_bp = bp = self.world.get_blueprint_library().filter('walker.pedestrian.*')

        # get 40 random spawn points for pedestrians
        pedestrian_navigation_points = []
        for i in range(number_of_pedestrians):
            point = carla.Transform()
            point.location = self.world.get_random_location_from_navigation()
            if point is not None:
                pedestrian_navigation_points.append(point)

        # add pedestrians: they will not move until we attach ai-controller to each one
        for i, transform in enumerate(pedestrian_navigation_points):
            walker_bp = random.choice(pedestrians_bp)
            walker = self.world.try_spawn_actor(walker_bp, transform)
            if walker is not None:
                self.pedestrians.append(walker)

        # attach ai-controller to each walker
        pedestrians_controller_bp = self.world.get_blueprint_library().find('controller.ai.walker')
        for w in range(len(self.pedestrians)):
            controller = self.world.spawn_actor(pedestrians_controller_bp, carla.Transform(), self.pedestrians[w])
            self.ai_controllers.append(controller)

        # put all ids (walkers and controllers) together in the same list to remove them from later from the world
        for i in range(len(self.pedestrians)):
            pedestrians_ids.append(self.pedestrians[i].id)
            pedestrians_ids.append(self.ai_controllers[i].id)

        # retrieve all elements in the world and places them in a list
        # all_pedestrians = []
        all_pedestrians = self.world.get_actors(pedestrians_ids)

        # wait server confirmation
        self.world.wait_for_tick()

        # enable automatic walk for pedestrian
        for ai in self.ai_controllers:
            ai.start()
            ai.go_to_location(self.world.get_random_location_from_navigation())
            ai.set_max_speed(1 + random.random())
        print("Len of pedestrians list: ", len(all_pedestrians))

    def setup_camera(self):
        """
        Spawns actor-camera to be used to render view.
        Sets calibration for client-side boxes rendering.
        """

        camera_transform = carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15))
        # attach the camera to the first vehicle
        self.camera = self.world.spawn_actor(self.camera_blueprint(), camera_transform, attach_to=self.vehicles[0])
        weak_self = weakref.ref(self)
        self.camera.listen(lambda image: weak_self().set_image(weak_self, image))

        calibration = np.identity(3)
        calibration[0, 2] = VIEW_WIDTH / 2.0
        calibration[1, 2] = VIEW_HEIGHT / 2.0
        calibration[0, 0] = calibration[1, 1] = VIEW_WIDTH / (2.0 * np.tan(VIEW_FOV * np.pi / 360.0))
        print('CALIB: ', calibration)
        self.camera.calibration = calibration

    def drive(self):
        """
        Will return True If ESCAPE is hit, otherwise False to end main loop.
        """
        print("############## IMG NAME IN DRIVE METH: ", str(self.image_name))
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            return True
        return False

    @staticmethod
    def set_image(weak_self, img):
        """
        Sets image coming from camera sensor.
        The self.capture flag is a mean of synchronization - once the flag is
        set, next coming image will be stored.
        """

        self = weak_self()
        if self.capture:
            self.image = img
            self.image_name = self.image.frame
            self.capture = False

    def save_img(self, coordinates_vehicles, coordinates_walkers):
        screen1 = pygame.display.get_surface()
        data1 = pygame.image.tostring(screen1, 'RGB')
        w1, h1 = screen1.get_size()

        # read image with PIL
        pil_img = Image.frombytes('RGB', (w1, h1), data1)

        # convert PIL Image to np-array
        img_array = np.array(pil_img)

        # reverse the image color format for opencv
        opencv_img = cv.cvtColor(img_array, cv.COLOR_RGB2BGR)

        name_edited = str(self.image_name) + '_edited' + '.png'
        name = str(self.image_name) + '.png'

        original_path = self.original_img_path / name
        copy_path = self.edited_img_path / name_edited

        v_annotation = []
        p_annotation = []

        print(coordinates_vehicles)
        for p in coordinates_vehicles:
            v_annotation_dict = {'P0': p[0], 'P1': p[1], 'P2': p[2], 'P3': p[3]}
            v_annotation.append(v_annotation_dict)

        print(coordinates_walkers)
        for p in coordinates_walkers:
            p_annotation_dict = {'P0': p[0], 'P1': p[1], 'P2': p[2], 'P3': p[3]}
            p_annotation.append(p_annotation_dict)

        self.custom_annotation['image_name'] = str(self.image_name) + '.png'
        self.custom_annotation['object_1']['identify'] = v_annotation
        self.custom_annotation['object_2']['identify'] = p_annotation
        self.create_annotation(self.custom_annotation, self.image_name)
        print(type(opencv_img))
        cv.imwrite(str(original_path), opencv_img)
        array_image = Draw_Box_On_Image.draw_box_1(opencv_img, coordinates_vehicles, (0, 0, 255))

        array_image = Draw_Box_On_Image.draw_box_1(opencv_img, coordinates_walkers, (0, 255, 0))
        cv.imwrite(str(copy_path), array_image)
        print("saved")

    def create_annotation(self, file_dict, img_frame):
        file_name = os.path.join(self.jsons_path, '{}.json'.format(img_frame))
        print('file name: ', file_name)
        with open(file_name, 'w', encoding='utf-8') as j_file:
            j_file.write(json.dumps(file_dict, indent=3, ensure_ascii=False))

    def render(self, display):
        """
        Transforms image from camera sensor and blits it to main pygame display.
        """

        if self.image is not None:
            array = np.frombuffer(self.image.raw_data, dtype=np.dtype("uint8"))
            array = np.reshape(array, (self.image.height, self.image.width, 4))
            array = array[:, :, :3]
            array = array[:, :, ::-1]
            surface = pygame.surfarray.make_surface(array.swapaxes(0, 1))
            display.blit(surface, (0, 0))

    def game_loop(self):
        """
        Main program loop.
        """

        try:
            pygame.init()

            self.client = carla.Client('127.0.0.1', 2000)
            self.client.set_timeout(2.0)
            self.world = self.client.get_world()

            self.create_and_spawn_vehicles(10)
            self.setup_camera()

            self.create_and_spawn_pedestrians(10)

            self.display = pygame.display.set_mode((VIEW_WIDTH, VIEW_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF)
            pygame_clock = pygame.time.Clock()

            self.set_synchronous_mode(True)

            while True:
                self.world.tick()

                self.capture = True
                pygame_clock.tick_busy_loop(20)

                self.render(self.display)
                vehicles_bbx, vehicles_ids, pedestrians_bbx, pedestrians_ids = ClientSideBoundingBoxes.get_bounding_boxes(
                    self.vehicles, self.pedestrians, self.camera)
                vehicles_bbx_cv, vehicle_id_cv, pedestrian_bbx_cv, pedestrian_id_cv = ClientSideBoundingBoxes.get_coords_boxes(
                    self.display, vehicles_bbx, vehicles_ids, pedestrians_bbx, pedestrians_ids)
                self.save_img(vehicles_bbx_cv, pedestrian_bbx_cv)

                pygame.display.flip()

                pygame.event.pump()
                if self.drive():
                    return

        finally:
            self.set_synchronous_mode(False)
            self.camera.destroy()
            # self.car.destroy()
            for vehicle in self.vehicles:
                vehicle.destroy()

            for ai in self.ai_controllers:
                ai.stop()
                ai.destroy()

            for pedestrian in self.pedestrians:
                pedestrian.destroy()
            print("Destroy actors done!")
            pygame.quit()


# ==============================================================================
# -- main() --------------------------------------------------------------------
# ==============================================================================


def main():
    """
    Initializes the client-side bounding box demo.
    """

    try:
        client = BasicSynchronousClient()
        client.game_loop()
    finally:
        print('EXIT')


if __name__ == '__main__':
    main()
