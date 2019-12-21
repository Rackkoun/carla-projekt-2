"""import carla
import sys
import os
from datetime import datetime
import time"""
import logging
import random


# source: https://github.com/carla-simulator/scenario_runner/blob/master/scenario_runner.py
# spurce: https://github.com/carla-simulator/carla/blob/master/PythonAPI/examples/synchronous_mode.py
class CustomVehicleManager(object):
    def __init__(self, client):
        self.client = client
        # self.delta_seconds = 1.0 / 30

        self.vehicle_lst = []
        self.camera_lst = []
        self.img_queue = []

        self.debug = None
        self.settings = None

    def on_spawn_vehicles(self, number_of_vehicle):
        tmp_var = number_of_vehicle
        world = self.client.get_world()
        world_map = world.get_map()
        vehicle_bp = world.get_blueprint_library().filter('vehicle.*')

        spawn_point_lst = world_map.get_spawn_points()
        number_of_points = len(spawn_point_lst)
        print('Number of points:  ', number_of_points)

        if tmp_var < number_of_points < 100:
            #random.shuffle(world_map.get_spawn_points())
            print("good^^ ")
        elif tmp_var > number_of_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, tmp_var, number_of_points)
            tmp_var = 100
        lst = []
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
        #vehicle_id_lst = self.client.apply_batch_sync(self.vehicle_lst)
        #for res in vehicle_id_lst:
        #    if res.error:
        #        logging.error(res.error)
        #    else:
        #        self.vehicle_lst.append(res.actor_id)

        # wait for tick
        world.wait_for_tick()

    def remove_all_vehicles(self):
        print("removing vehicles...")
        for actor in self.vehicle_lst:
            actor.destroy()
        #self.client.apply_batch_sync([actor.destroy() for actor in self.vehicle_lst])
        print("World reloaded vehicle")