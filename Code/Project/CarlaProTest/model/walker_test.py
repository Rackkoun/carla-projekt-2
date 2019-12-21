"""
:@authors:
"""

import random
import logging
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

        spawn_point_lst = world_map.get_spawn_points()
        number_of_points = len(spawn_point_lst)
        print('Number of points (W):  ', number_of_points)

        # lst = []
        if tmp_var < number_of_points < 50:
            #random.shuffle(world_map.get_spawn_points())
            print("feel goog (^ ^)")
        elif tmp_var > number_of_points:
            msg = 'requested %d vehicles, but could only find %d spawn points'
            logging.warning(msg, tmp_var, number_of_points)
            tmp_var = 50

        for _, transform in enumerate(spawn_point_lst):
            if _ >= tmp_var:
                break

            print("choosing a walker on the library...")
            walker_bp = random.choice(bp)
            walker = world.spawn_actor(walker_bp, transform)
            print(_, "Walkers added")
            self.walker_lst.append(walker)
        #print("apply batch for walker step 1")
        #results_1 = self.client.apply_batch_sync(self.walker_lst)
        #print("RES_1: ", results_1)
        #for res in results_1:
        #    if res.error:
        #        logging.error(res.error)
        #    else:
        #        print("OK : ", res)
        #        #self.vehicle_lst.append(res.actor_id)
        print("adding controller to walker")
        for i in range(tmp_var):
            walker_ai = world.spawn_actor(ai_bp, Transform(), self.walker_lst[i])
            walker_goal = world.get_random_location_from_navigation()
            walker_ai.start()
            walker_ai.go_to_location(walker_goal)
            walker_ai.set_max_speed(1 + random.random())
            self.walker_ai_lst.append(walker_ai)
        #print("apply batch AI, step 2")
        #results_2 = self.client.apply_batch_sync(self.walker_ai_lst)
        #for res in results_2:
        #    if res.error:
        #        logging.error(res.error)
        #    else:
        #        print("Ok Ok: ", res)
        print("list content")
        print("waiting for server answer...")
        world.wait_for_tick()
        print("done")
        print(self.walker_ai_lst)
        print(self.walker_lst)

    def on_remove_walkers(self):
        # self.world = client.get_world()
        print("stopping walkers...")
        for w in self.walker_ai_lst:
            # if w.is_alive:
            w.stop()

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
        self.client.reload_world()
        print("World reloaded")
