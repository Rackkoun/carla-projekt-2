"""
:@authors: Zanguim K. L, Fozing Y. W., Tchana D. R.
"""
import glob
import os
import random
import logging
import sys
try:
    sys.path.append(glob.glob('../carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla
from carla import Transform

"""
 results = client.apply_batch_sync(lst, True)
TypeError: No registered converter was able to produce a C++ rvalue of type carla::rpc::Command from this Python object of type Walker
Erreur produite lorsque la liste n est pas de carla command
"""


class CustomPedestrianManager(object):

    def __init__(self, client):
        self.client = client
        # self.delta_seconds = 1.0 / 30

        self.walkers = []  # to retrieve actors in the world for remove action
        self.walker_lst = []
        self.walkers_id = []
        self.walker_ai_lst = []

        self.camera_lst = []
        self.img_queue = []

        self.debug = None
        self.settings = None

    # Location is important to spawn walkers in the world
    def on_spawn_walkers(self, number_of_walkers):
        tmp_var = number_of_walkers
        world = self.client.get_world()
        world_map = world.get_map()
        bp = world.get_blueprint_library().filter('walker.pedestrian.*')
        ai_bp = world.get_blueprint_library().find('controller.ai.walker')

        spawn_point_lst = []
        for i in range(50):
            spawn_point = carla.Transform()
            spawn_point.location = world.get_random_location_from_navigation()
            if (spawn_point.location != None):
                spawn_point_lst.append(spawn_point)

        #spawn_point_lst = world_map.get_spawn_points()
        number_of_points = len(spawn_point_lst)
        print('Number of points (W):  ', number_of_points)

        #if tmp_var < number_of_points < 50:
        if tmp_var < number_of_points:
            #random.shuffle(world_map.get_spawn_points())
            print("feel goog (^ ^)")
        elif tmp_var > number_of_points:
            msg = 'requested %d Walkers, but could only find %d spawn points'
            logging.warning(msg, tmp_var, number_of_points)
            #tmp_var = 50
            tmp_var=number_of_points

        for _, transform in enumerate(spawn_point_lst):
            if _ >= tmp_var:
                break

            print("choosing a walker on the library...")
            walker_bp = random.choice(bp)

            walker = world.try_spawn_actor(walker_bp, transform)
            if walker != None:
                print(_, "Walkers added",walker_bp.id)
                print("walker=",walker)
                self.walker_lst.append(walker)
            else:
                print(_, "Walkers NOT added")
                print("walker=",walker)

        print("adding controller to walker")
        control_walker_lst = []
        for i in range (len(self.walker_lst)):
            control = world.spawn_actor(ai_bp, Transform(), self.walker_lst[i])
            control_walker_lst.append(control)

        all_id=[]

        for i in range(len(self.walker_lst)):
            print("control:",control_walker_lst[i].id)
            print("walker:",self.walker_lst[i].id)
            all_id.append(control_walker_lst[i].id)
            all_id.append(self.walker_lst[i].id)

        all_actors = world.get_actors(all_id)

        print("all actors:", all_actors)

        world.wait_for_tick()

        print("Starting the AI Control")

        for i in range(0, len(all_actors), 2):
            # start walker
            all_actors[i].start()
            # set walk to random point
            all_actors[i].go_to_location(world.get_random_location_from_navigation())
            # random max speed
            all_actors[i].set_max_speed(1 + random.random())

    def on_remove_walkers(self):
        # self.world = client.get_world()
        print("stopping walkers...")
        for w in self.walker_ai_lst:
            # if w.is_alive:
            w.stop()
            w.destroy()

        print("AI stopped")
        print("destroying walkers...")
        # walkers = self.world.get_actors(self.walkers)
        world = self.client.get_world()
        for walker in self.walkers:
            actor = world.get_actor(walker.actor_id)
            if actor.is_alive:
                actor.destroy()
        print("destroyed")
        self.walkers.clear()
        self.walker_ai_lst.clear()
        self.walkers_id.clear()
        self.walker_lst.clear()
        print("Lists cleared...")
