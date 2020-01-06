"""
:@authors: Zanguim K. L, Fozing Y. W., Tchana D. R.
"""
import glob
import logging
import os
import random
import sys

try:
    sys.path.append(glob.glob('../carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# source: https://github.com/carla-simulator/scenario_runner/blob/master/scenario_runner.py
# source: https://github.com/carla-simulator/carla/blob/master/PythonAPI/examples/synchronous_mode.py
# source: https://github.com/carla-simulator/carla/blob/master/Docs/configuring_the_simulation.md
# source: (create directory): https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
# source: (datetime doc): https://docs.python.org/3/library/datetime.html


class CustomVehicleManager(object):
    """
    Class to generate Vehicles and spawn them in the current world
    :param client: to get the current opened server for the simulation
    :param vehicle_lst: list to added spawned actors in the current world
    """
    def __init__(self, client):
        self.client = client
        self.vehicle_lst = []

    def on_spawn_vehicles(self, number_of_vehicle):
        """
        Method to spawn vehicles in the the current world
        :param number_of_vehicle: the number of vehicles we want to spawn in the world
        """
        tmp_var = number_of_vehicle
        world = self.client.get_world()  # get the current world through the connected client
        world_map = world.get_map()      # get the map that describe the current world
        vehicle_bp = world.get_blueprint_library().filter('vehicle.*')  # get all vehicle in the blueprint library

        spawn_point_lst = world_map.get_spawn_points()  # get the recommended spawn-points in the world map
        number_of_points = len(spawn_point_lst)
        print('Number of points:  ', number_of_points)

        if tmp_var < number_of_points < 100:  # give a maximum to avoid collision while spawning vehicles
            print("good^^ ")
        elif tmp_var > number_of_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, tmp_var, number_of_points)
            tmp_var = 100

        for _, transform in enumerate(spawn_point_lst):  # a recommended spawn point is a Carla-Transform-datatype
            if _ >= tmp_var:
                break
            bp = random.choice(vehicle_bp)  # select randomly a vehicle in the blueprint library
            vehicle = world.spawn_actor(bp, transform)  # add it in the world a the given location 'transform'
            vehicle.set_autopilot()  # then enable auto pilot
            print("i: ", _)
            print("Transform: ", transform)
            self.vehicle_lst.append(vehicle)
            print("Vehicle added: ", vehicle)
            print("id ", vehicle.id, " added")

        print("end of methode spawn for vehicles")
        world.wait_for_tick()

    def remove_all_vehicles(self):
        """
        Destroy all saved vehicle in the list and the clear the list
        :return:
        """
        print("removing vehicles...")
        for actor in self.vehicle_lst:
            actor.destroy()
        print("vehicles destroyed!")
        self.vehicle_lst.clear()
