#!/usr/bin/env python

# Copyright (c) 2019 Aptiv
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.

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
import json
import os
import sys
import threading
import time
from datetime import datetime

#indicate the location of the carla egg file, in this case in the "carla-egg" folder
try:
    sys.path.append(glob.glob('carla_egg/carla-*%d.%d-%s.egg' % (
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
import string
from PIL import Image

from  data_file_processing import process_data_file
from CUSANI import Toplevel1

import cv2

try:
    import pygame
    from pygame.locals import K_ESCAPE
    from pygame.locals import K_SPACE
    from pygame.locals import K_q #turn left
    from pygame.locals import K_d #turn right
    from pygame.locals import K_s #brake
    from pygame.locals import K_z #accelerate
    from pygame.locals import K_f #handbrake
    from pygame.locals import K_p #toggle automatic or manual control, always automatic control at the beginning
except ImportError:
    raise RuntimeError('cannot import pygame, make sure pygame package is installed')

try:
    import numpy as np
except ImportError:
    raise RuntimeError('cannot import numpy, make sure numpy package is installed')

VIEW_WIDTH = 1920//2
VIEW_HEIGHT = 1080//2

#size of the images
#VIEW_WIDTH_1 = 1024
#VIEW_HEIGHT_1 = 768

VIEW_WIDTH_1 = 1280
VIEW_HEIGHT_1 = 960


VIEW_FOV = 90

BB_COLOR = (248, 64, 24)
BB_COLOR_2 = (0, 255, 0)


# ==============================================================================
# -- ClientSideBoundingBoxes ---------------------------------------------------
# ==============================================================================


#here with calculate the Bounding boxes coordinates
class ClientSideBoundingBoxes(object):
    """
    This is a module responsible for creating 3D bounding boxes and drawing them
    client-side on pygame surface.
    """

    @staticmethod
    def get_bounding_boxes(vehicles, camera):
        """
        Creates 3D bounding boxes based on carla vehicle list and camera.
        """

        bounding_boxes = [ClientSideBoundingBoxes.get_bounding_box(vehicle, camera) for vehicle in vehicles]
        # filter objects behind camera
        bounding_boxes = [bb for bb in bounding_boxes if all(bb[:, 2] > 0) and all(bb[:, 2] <= 70)]
        return bounding_boxes

    #not use, just for test
    @staticmethod
    def draw_bounding_boxes(display, bounding_boxes,type_object):
        """
        Draws bounding boxes on pygame display.
        """

        bb_surface = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
        bb_surface.set_colorkey((0, 0, 0))
        for bbox in bounding_boxes:
            points = [(int(bbox[i, 0]), int(bbox[i, 1])) for i in range(8)]

            #print("points shape:",len(points))
            #print("type points:",type(points))
            #print("one point type:",type(points[0]))
            #print(points)
            min_x=points[0][0]
            min_y=points[0][1]
            max_x=points[0][0]
            max_y=points[0][1]
            for point in points:
                if(min_x >= 0 ):
                    if(point[0]>=0 and point[0]<=min_x):
                        min_x=point[0]
                else:
                    if(point[0] >= 0):
                        min_x=point[0]

                if (point[0] >= 0 and point[0] >= max_x):
                    max_x = point[0]

                if (point[1] <= min_y):
                    min_y = point[1]
                if (point[1] >= max_y):
                    max_y = point[1]
            if(min_x < 0 or min_x == max_x):
                pass
                #print("unable to find extrema values:",min_x,max_x,min_y,max_y)
            else:
                #print("rectangle points:", min_x, max_x, min_y, max_y)
                point1=(min_x,min_y)
                point2=(min_x,max_y)
                point3=(max_x,max_y)
                point4=(max_x,min_y)

                if(type_object==1):
                    pygame.draw.line(bb_surface, BB_COLOR, point1, point2)
                    pygame.draw.line(bb_surface, BB_COLOR, point2, point3)
                    pygame.draw.line(bb_surface, BB_COLOR, point3, point4)
                    pygame.draw.line(bb_surface, BB_COLOR, point4, point1)

                else:
                    pygame.draw.line(bb_surface, BB_COLOR_2, point1, point2)
                    pygame.draw.line(bb_surface, BB_COLOR_2, point2, point3)
                    pygame.draw.line(bb_surface, BB_COLOR_2, point3, point4)
                    pygame.draw.line(bb_surface, BB_COLOR_2, point4, point1)
                #pygame.draw.line(bb_surface, BB_COLOR, points[3], points[0])

            # draw lines
            # base
            # pygame.draw.line(bb_surface, BB_COLOR, points[0], points[1])
            # pygame.draw.line(bb_surface, BB_COLOR, points[0], points[1])
            # pygame.draw.line(bb_surface, BB_COLOR, points[1], points[2])
            # pygame.draw.line(bb_surface, BB_COLOR, points[2], points[3])
            # pygame.draw.line(bb_surface, BB_COLOR, points[3], points[0])
            # # top
            # pygame.draw.line(bb_surface, BB_COLOR, points[4], points[5])
            # pygame.draw.line(bb_surface, BB_COLOR, points[5], points[6])
            # pygame.draw.line(bb_surface, BB_COLOR, points[6], points[7])
            # pygame.draw.line(bb_surface, BB_COLOR, points[7], points[4])
            # # base-top
            # pygame.draw.line(bb_surface, BB_COLOR, points[0], points[4])
            # pygame.draw.line(bb_surface, BB_COLOR, points[1], points[5])
            # pygame.draw.line(bb_surface, BB_COLOR, points[2], points[6])
            # pygame.draw.line(bb_surface, BB_COLOR, points[3], points[7])
        display.blit(bb_surface, (0, 0))

    #get the box 2D coordinate from the Box 2D verticles
    @staticmethod
    def get_bounding_2d_boxes_coordinates(bounding_boxes, type_object):
        """
                Draws bounding boxes on pygame display.
                """
        coordinates=[]
        
        #obtain for each 3D box his 2D box coordinate
        for bbox in bounding_boxes:
            points = [(int(bbox[i, 0]), int(bbox[i, 1])) for i in range(8)]

            #print("points shape:", len(points))
            #print("type points:", type(points))
            #print("one point type:", type(points[0]))
            #print(points)
            min_x = points[0][0]
            min_y = points[0][1]
            max_x = points[0][0]
            max_y = points[0][1]
            for point in points:
                if (min_x >= 0):
                    if (point[0] >= 0 and point[0] <= min_x):
                        min_x = point[0]
                else:
                    if (point[0] >= 0):
                        min_x = point[0]

                if (point[0] >= 0 and point[0] >= max_x):
                    max_x = point[0]

                if (point[1] <= min_y):
                    min_y = point[1]
                if (point[1] >= max_y):
                    max_y = point[1]
            if (min_x < 0 or min_x == max_x):
                pass
                #print("unable to find extrema values:", min_x, max_x, min_y, max_y)
            else:
                #check if the point are located in our picture
                if(min_x <= VIEW_WIDTH_1) and (max_x <= VIEW_WIDTH_1) and (min_y <= VIEW_HEIGHT_1) and (max_y <= VIEW_HEIGHT_1): 

                    print("rectangle points:", min_x, max_x, min_y, max_y)
                    point1 = (min_x, min_y)
                    point2 = (min_x, max_y)
                    point3 = (max_x, max_y)
                    point4 = (max_x, min_y)

                    if(type_object==1):
            
                        #check if the vehicle are not too far from the scene
                        if((max_x-min_x)>=18) and ((max_y-min_y)>=20):

                            coordinates.append(point1+point3)
                        else:
                            print("car coordinates too far from the scene:",min_x, max_x, min_y, max_y)
                    else:#check if the pedestrian (walkers) are not too far from the scene
                        if ((max_x - min_x) >= 8) and ((max_y - min_y) >= 12):

                            coordinates.append(point1 + point3)
                        else:
                            print("walker coordinates too far from the scene:", min_x, max_x, min_y, max_y)
                else:
                    print("Coordinates of object out of the image:",min_x,max_x,min_y,max_y)
                    #pygame.draw.line(bb_surface, BB_COLOR, point1, point2)
                    #pygame.draw.line(bb_surface, BB_COLOR, point2, point3)
                    #pygame.draw.line(bb_surface, BB_COLOR, point3, point4)
                    #pygame.draw.line(bb_surface, BB_COLOR, point4, point1)
        return coordinates

    @staticmethod


    def get_bounding_box(vehicle, camera):
        """
        Returns 3D bounding box for a vehicle based on camera view.
        """

        bb_cords = ClientSideBoundingBoxes._create_bb_points(vehicle)
        cords_x_y_z = ClientSideBoundingBoxes._vehicle_to_sensor(bb_cords, vehicle, camera)[:3, :]
        cords_y_minus_z_x = np.concatenate([cords_x_y_z[1, :], -cords_x_y_z[2, :], cords_x_y_z[0, :]])
        bbox = np.transpose(np.dot(camera.calibration, cords_y_minus_z_x))
        camera_bbox = np.concatenate([bbox[:, 0] / bbox[:, 2], bbox[:, 1] / bbox[:, 2], bbox[:, 2]], axis=1)
        return camera_bbox

    @staticmethod
    def _create_bb_points(vehicle):
        """
        Returns 3D bounding box for a vehicle.
        """

        cords = np.zeros((8, 4))
        extent = vehicle.bounding_box.extent
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
    def _vehicle_to_sensor(cords, vehicle, sensor):
        """
        Transforms coordinates of a vehicle bounding box to sensor.
        """

        world_cord = ClientSideBoundingBoxes._vehicle_to_world(cords, vehicle)
        sensor_cord = ClientSideBoundingBoxes._world_to_sensor(world_cord, sensor)
        return sensor_cord

    @staticmethod
    def _vehicle_to_world(cords, vehicle):
        """
        Transforms coordinates of a vehicle bounding box to world.
        """

        bb_transform = carla.Transform(vehicle.bounding_box.location)
        bb_vehicle_matrix = ClientSideBoundingBoxes.get_matrix(bb_transform)
        vehicle_world_matrix = ClientSideBoundingBoxes.get_matrix(vehicle.get_transform())
        bb_world_matrix = np.dot(vehicle_world_matrix, bb_vehicle_matrix)
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

#interaction mit carla simulator
class BasicSynchronousClient(object):
    """
    Basic implementation of a synchronous client.
    """

    def __init__(self):
        self.client = None
        self.world = None
        self.camera = None
        self.car = None

        self.display = None
        self.image = None
        self.capture = True

        self.autopilot=1


        self.parent_original_img_path = process_data_file.read_List_Folder_Settings()[0] #where original images are stored
        self.parent_treated_img_path = process_data_file.read_List_Folder_Settings()[1] #where treated images are stored
        self.parent_json_path = process_data_file.read_List_Folder_Settings()[2] #where Json files are stored


    def camera_blueprint(self):
        """
        Returns camera blueprint.
        """

        camera_bp = self.world.get_blueprint_library().find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', str(VIEW_WIDTH_1))
        camera_bp.set_attribute('image_size_y', str(VIEW_HEIGHT_1))
        camera_bp.set_attribute('fov', str(VIEW_FOV))
        #camera_bp.set_attribute('sensor_tick', str(7))
        return camera_bp

    def set_synchronous_mode(self, synchronous_mode):
        """
        Sets synchronous mode.
        """

        settings = self.world.get_settings()
        settings.synchronous_mode = synchronous_mode
        self.world.apply_settings(settings)

    def set_weather(self):
        weather= carla.WeatherParameters(cloudyness=0.0000,
                                               precipitation=0.000000,
                                               precipitation_deposits=0.0000,
                                               wind_intensity=0.000000,
                                               sun_azimuth_angle=80.340317,
                                               sun_altitude_angle=53.907822)
        self.world.set_weather(weather)

    def setup_car(self):
        """
        Spawns actor-vehicle to be controled.
        """

        #car_bp = self.world.get_blueprint_library().filter('vehicle.*')[1]
        autos=self.world.get_blueprint_library().filter('vehicle.*')
        bikes=[]
        cars=[]
        for x in autos:
            if int(x.get_attribute('number_of_wheels')) == 2:
                bikes.append(x)
            if int(x.get_attribute('number_of_wheels')) == 4:
                cars.append(x)
        if(len(bikes)>=1):
            car_bp=bikes[0] #just wanted that the principal actor should be a bike or motobike
        else:
            car_bp=cars[0] #if there is no bike, we take a car as principal actor

        car_bp.set_attribute('role_name','hero') #setting the previous selected object (bike oder car) as principal actor, in order to identify him later
        location = random.choice(self.world.get_map().get_spawn_points()) #selecting one location to spawn our principal actor
        self.car = self.world.spawn_actor(car_bp, location) #spawning our principal actor

    def setup_camera(self):
        """
        Spawns actor-camera to be used to render view.
        Sets calibration for client-side boxes rendering.
        """

        camera_transform = carla.Transform(carla.Location(x=-5.5, z=2.8), carla.Rotation(pitch=-15))
        self.camera = self.world.spawn_actor(self.camera_blueprint(), camera_transform, attach_to=self.car) #attaching the camera to our principal actor
        weak_self = weakref.ref(self)
        self.camera.listen(lambda image: weak_self().set_image(weak_self, image)) #function set_image call every time a picture is taken, but actually not use
        #self.camera.listen(lambda image: weak_self().set_image(weak_self, image))
        
        #calibrating the camera
        calibration = np.identity(3)
        calibration[0, 2] = VIEW_WIDTH_1 / 2.0
        calibration[1, 2] = VIEW_HEIGHT_1 / 2.0
        calibration[0, 0] = calibration[1, 1] = VIEW_WIDTH_1 / (2.0 * np.tan(VIEW_FOV * np.pi / 360.0))
        self.camera.calibration = calibration

    #saving the original pictures and the Json files in the appropriate folder
    def save_img_and_json_process(self):
        vehicles = self.world.get_actors().filter('vehicle.*') #getting all thevehicle in the world
        walkers = self.world.get_actors().filter('walker.pedestrian.*') #getting all the walkers in the world
        print("number of vehicles:", len(vehicles))
        print("number of walkers:", len(walkers))
        bounding_boxes_vehicles = ClientSideBoundingBoxes.get_bounding_boxes(vehicles, self.camera) #get for all the vehicles thier 3D Bounding Boxes
        bounding_boxes_walkers = ClientSideBoundingBoxes.get_bounding_boxes(walkers, self.camera) #get for all the walkers thier 3D Bounding Boxes
        print("all boxes vehicles len", len(bounding_boxes_vehicles))
        print("all boxes walkers len", len(bounding_boxes_walkers))
        # print("all boxes:",bounding_boxes)
        # ClientSideBoundingBoxes.draw_bounding_boxes(self.display, bounding_boxes)
        
        #get for all the 3D boxes the equivalent 2D boxes
        all_boxes_coordinate_vehicles = ClientSideBoundingBoxes.get_bounding_2d_boxes_coordinates(
            bounding_boxes_vehicles, 1) 
        all_boxes_coordinate_walkers = ClientSideBoundingBoxes.get_bounding_2d_boxes_coordinates(bounding_boxes_walkers,
                                                                                                 0)

        print("number of boxes vehicles to draw", len(all_boxes_coordinate_vehicles))
        print("number of boxes walkers to draw", len(all_boxes_coordinate_walkers))

        # print("all boxcoordinate",all_boxes_coordinates)
        # print("len all boxcoordinate", len(all_boxes_coordinates))
        # print("type all boxcoordinate", type(all_boxes_coordinates))
        # print("all boxcoordinate[0]", all_boxes_coordinates[0])
        # print("type all boxcoordinate[0]", type(all_boxes_coordinates[0]))
        self.save_img_and_json(all_boxes_coordinate_vehicles, all_boxes_coordinate_walkers) #send the 2D Boxes coordinates to be saved in a Json file

    def control(self, car):
        """
        Applies control to main car based on pygame pressed keys.
        Will return True If ESCAPE is hit, otherwise False to end main loop.
        """




        keys = pygame.key.get_pressed() #record the pressed key
        if keys[K_ESCAPE]: #close the pygame window
            return True

        control = car.get_control()
        #control.throttle = 0
        if keys[K_f]:
            self.save_img_and_json_process() #save the picture we are seeing in the pygame window

        if keys[K_p]: #activate/deactivate the autopilot
            #control.throttle = 1
            self.autopilot=(self.autopilot+1)
            self.autopilot=self.autopilot%2
            print("autopilot value:",self.autopilot)
            if(self.autopilot==1): #autopilot activated
                car.set_autopilot(True)

                control.gear = 1 if control.reverse else -1
                print("Autopilot Enabled")
                print("car trottle:",control.throttle)
                #print("autopilot enabled")
            else: #autopilot deactivated
                car.set_autopilot(False)
                print("Autopilot Disabled")

        if(self.autopilot == 0): #if autopilot is deactivated

            control = car.get_control()
            control.throttle = 0
            if keys[K_z]: #accelerate
                control.throttle = 1
                control.reverse = False
            elif keys[K_s]: #brake
                control.throttle = 1
                control.reverse = True
            if keys[K_q]: #turn left
                control.steer = max(-1., min(control.steer - 0.05, 0))
            elif keys[K_d]:# turn right
                control.steer = min(1., max(control.steer + 0.05, 0))
            else:
                control.steer = 0
            control.hand_brake = keys[K_SPACE] #hand brake

            car.apply_control(control)
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
            #self.save_image_process()

            self.capture = False

    #this function save the take image and send data to save the coordinates in a Json file
    def save_img_and_json(self, coordinates_vehicles, coordinates_walkers):
        #capture all what appear in the screen
        screen1 = pygame.display.get_surface()
        data1 = pygame.image.tostring(screen1, 'RGB')
        w1, h1 = screen1.get_size()
        img1 = Image.frombytes('RGB', (w1, h1), data1)

        #img1=self.image
        print("image type:",type(img1))

        letters = string.ascii_letters+string.digits
        name = ''.join(random.choice(letters) for i in range(8)) #generate random string with 5 letters

        name_1 = name + '_Treated' + '.jpeg' #name of the Treated image
        name_2 = name + '_Json' + '.json'  #name of the Json file

        test_name = name + '_Original' + '.jpeg'  # name of the original image

        name = name + '_Original' + '.jpeg' #name of the original image

        #name = name + '.jpeg'


        this_path = os.path.dirname(os.path.abspath(__file__))
        savepath = os.path.join(this_path, self.parent_original_img_path, '{}'.format(name)) #path of the original images
        savepath1=os.path.join(this_path, self.parent_treated_img_path, '{}'.format(name_1)) #path of the treated images
        savepath2 = os.path.join(this_path, self.parent_json_path, '{}'.format(name_2)) #path of the Json files

        test_path=os.path.join(this_path, self.parent_original_img_path, '{}'.format(test_name))

        print("savepath original=", savepath)
        print("savepath Treated=", savepath1)
        print("savepath Json=", savepath2)

        print("Test Path:",test_path)

        img1.save(savepath, 'JPEG') #saving the original image

        process_data_file.save_json(coordinates_vehicles, coordinates_walkers, savepath2) #sending coordinate to create the Json file

        #self.image.save_to_disk(test_path)

        # my_image=cv2.imread(savepath)
        #
        # array_image=process_data_file.draw_box_1(my_image,coordinates_vehicles,(0,0,255))
        #
        # array_image = process_data_file.draw_box_1(array_image, coordinates_walkers,(0,255,0))
        #
        # process_data_file.save_image(savepath1,array_image)
        #





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

    #here we create a thread, to wait a specific time before taking images
    def run(self):
        #wait=5
        wait=None
        saving_Thread=threading.Thread(target=self.save_image_tread_process,args=(wait,))
        print("saving thread started with wait time:",wait)
        saving_Thread.start()
        #saving_Thread.join()

    #this function wait the defined time before taking pictures and send them to be save
    def save_image_tread_process(self,wait):
        if wait!=None:
            while(True):
                time.sleep(int(wait))
                self.save_img_and_json_process() #function initiate the process to save the image and the json file


    def game_loop(self):
        """
        Main program loop.
        """

        try:

            pygame.init()

            self.client = carla.Client('127.0.0.1', 2000) #carla client connect on localhost on port 2000
            self.client.set_timeout(2.0)
            self.world = self.client.get_world() #get the worl in the carla simulator
            #self.world= self.client.load_world("Town02") #we culd also load a specific world

            self.setup_car()
            self.setup_camera()

            self.display = pygame.display.set_mode((VIEW_WIDTH_1, VIEW_HEIGHT_1), pygame.HWSURFACE | pygame.DOUBLEBUF)
            pygame_clock = pygame.time.Clock()

            self.set_synchronous_mode(True)

            self.set_weather()



            #walkers = self.world.get_actors().filter('walker.pedestrian.*')
            #vehicles = self.world.get_actors().filter('vehicle.*')

            #retrieved the previuos defined principal actor
            nb_hero=0
            for actor in self.world.get_actors():
                if actor.attributes.get('role_name') == 'hero':
                    print("Hero player found:", actor)
                    actor.set_autopilot(True) #activate the autopilot of this actor
                    nb_hero=nb_hero+1

            if(nb_hero==0):
                print("Hero player not found")
                print("number of hero :", nb_hero)
            else:
                print("Hero player found")
                print("number of hero :",nb_hero)

            while True:
                self.world.tick()

                self.capture = True
                pygame_clock.tick_busy_loop(20)

                self.render(self.display)
                # bounding_boxes_vehicles = ClientSideBoundingBoxes.get_bounding_boxes(vehicles, self.camera)
                # bounding_boxes_walkers = ClientSideBoundingBoxes.get_bounding_boxes(walkers, self.camera)
                # ClientSideBoundingBoxes.draw_bounding_boxes(self.display, bounding_boxes_vehicles,1)
                # ClientSideBoundingBoxes.draw_bounding_boxes(self.display, bounding_boxes_walkers,0)

                pygame.display.flip()

                pygame.event.pump()
                if self.control(self.car):
                    return

        finally:
            self.set_synchronous_mode(False)
            #destroy the camera and the car before exiting pygame
            self.camera.destroy()
            self.car.destroy()
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
        client.run() #start the Thread
        client.game_loop()

    finally:
        print('EXIT')


if __name__ == '__main__':
    main()
