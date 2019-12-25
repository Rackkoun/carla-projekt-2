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
from carla import BoundingBox, Vector3D, Color


# source: https://github.com/carla-simulator/scenario_runner/blob/master/scenario_runner.py
# spurce: https://github.com/carla-simulator/carla/blob/master/PythonAPI/examples/synchronous_mode.py
# source: https://github.com/carla-simulator/carla/blob/master/Docs/configuring_the_simulation.md

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
            cloudyness=1.0,
            precipitation=1.0,
            sun_altitude_angle=80.0)
        # get the world settings and check if synchronized_mode is enable
        self.settings = world.get_settings()

        # if self.settings.synchronous_mode is not True:
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
        sensor_bp.set_attribute('sensor_tick', '3.0')
        loc = Location(x=-5.5, y=0.0, z=2.8)
        rot = Rotation(pitch=-15)

        transform = Transform(loc, rot)
        sensor = world.spawn_actor(sensor_bp, transform, attach_to=vehicle)
        self.camera_lst.append(sensor)
        print("sensor appended..", sensor)

    def on_debug_vehicle(self, world, world_snapshot, actor):
        print("starting debugging...")
        # enable debugging
        self.debug = world.debug
        # retrieve object in the world snapshot through it id
        actor_snapshot = world_snapshot.find(actor.id)
        retrieved_actor = world.get_actor(actor_snapshot.id)
        if retrieved_actor.id == actor_snapshot.id:
            print("Actor retrieved: ", retrieved_actor)
            # get location and draw box
            current_location = actor_snapshot.get_transform().location
            box = retrieved_actor.bounding_box
            box.extent.z += 0.5
            self.debug.draw_box(
                box=BoundingBox(
                    current_location,
                    Vector3D(
                        x=box.extent.x,
                        y=box.extent.y,
                        z=box.extent.z
                    )
                ),
                rotation=actor_snapshot.get_transform().rotation,
                thickness=0.11,
                color=Color(255, 10, 5),
                life_time=0.0001
            )
            ####### Draw ID as string #####
            string_position = current_location
            string_position.z += 2.2
            self.debug.draw_string(
                location = current_location,
                text="Id: {}".format(actor_snapshot.id),
                draw_shadow=False,
                color=Color(254, 254, 254)
            )
        return world_snapshot

    def remove_all_vehicles(self):
        print("removing vehicles...")
        for actor in self.vehicle_lst:
            actor.destroy()
        # self.client.apply_batch_sync([actor.destroy() for actor in self.vehicle_lst])
        print("vehicles destroyed!")
