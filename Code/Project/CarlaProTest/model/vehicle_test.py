"""import carla
import sys
import os
from datetime import datetime
import time"""
import logging
import random
import time
from queue import Queue
from carla import Transform, Location, Rotation
from carla import WeatherParameters

# source: https://github.com/carla-simulator/scenario_runner/blob/master/scenario_runner.py
# spurce: https://github.com/carla-simulator/carla/blob/master/PythonAPI/examples/synchronous_mode.py
class CustomVehicleManager(object):
    def __init__(self, client):
        self.client = client
        self.delta_seconds = 1.0 / 30

        self.vehicle_lst = []
        self.camera_lst = []
        self.img_queue = []

        self.debug = None
        self.settings = None
        self.frame = None

        self.on_setting_world()

    def on_spawn_vehicles(self, number_of_vehicle):
        tmp_var = number_of_vehicle
        world = self.client.get_world()
        world_map = world.get_map()
        vehicle_bp = world.get_blueprint_library().filter('vehicle.*')

        spawn_point_lst = world_map.get_spawn_points()
        number_of_points = len(spawn_point_lst)
        print('Number of points:  ', number_of_points)

        if tmp_var < number_of_points < 100:
            print("good^^ ")
        elif tmp_var > number_of_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, tmp_var, number_of_points)
            tmp_var = 100

        for _, transform in enumerate(spawn_point_lst):
            if _ >= tmp_var:
                break
            bp = random.choice(vehicle_bp)
            vehicle = world.spawn_actor(bp, transform)
            vehicle.set_autopilot()
            print("i: ", _)
            print("Transform: ", transform)
            self.vehicle_lst.append(vehicle)
            print("Vehicle added: ", vehicle)
            if _ == (tmp_var - 1):
                print("trying to attatch sensor to the last vehicle: ", _)
                self.on_attach_senor_to_vehicle(vehicle)
        print("end of methode spawn for vehicles")
        world.wait_for_tick()
        print("tick in the method reached")
        self.on_starting_listening()

    def on_starting_listening(self):
        print("listening data...")
        sensor = self.camera_lst[0]
        print("starting listening...")
        sensor.listen(lambda img: img.save_to_disk('res/screenshots/%04d.png' % img.frame))
        print("saving state: ", sensor.is_listening)

    def on_setting_world(self):
        # retrieve the world through the current client
        world = self.client.get_world()
        weather = WeatherParameters(
            cloudyness=9.0,
            precipitation=3.0,
            sun_altitude_angle=80.0)
        # get the world settings and check if synchronized_mode is enable
        self.settings = world.get_settings()

        #if self.settings.synchronous_mode is not True:
        #    print("enabling synchronized mode...")
        #    self.settings.synchronous_mode = True
        #    self.settings.fixed_delta_seconds = self.delta_seconds
        world.set_weather(weather)
        # get the frame with the settings
        self.frame = world.apply_settings(self.settings)

    def on_attach_senor_to_vehicle(self, vehicle, sensor_type='sensor.camera.rgb'):
        world = self.client.get_world()
        bp = world.get_blueprint_library()
        sensor_bp = bp.find(sensor_type)
        sensor_bp.set_attribute('image_size_x', '680')
        sensor_bp.set_attribute('image_size_y', '600')
        sensor_bp.set_attribute('fov', '110')
        sensor_bp.set_attribute('sensor_tick', '2.0')
        loc = Location(x=-5.5, y=0.0, z=2.8)
        rot = Rotation(pitch=-15)

        transform = Transform(loc, rot)
        sensor = world.spawn_actor(sensor_bp, transform, attach_to=vehicle)
        self.camera_lst.append(sensor)
        print("sensor appended..", sensor)

    def remove_all_vehicles(self):
        print("removing vehicles...")
        for actor in self.vehicle_lst:
            actor.destroy()
        # self.client.apply_batch_sync([actor.destroy() for actor in self.vehicle_lst])
        print("World reloaded vehicle")
