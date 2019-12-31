"""import carla
import sys
import os
from datetime import datetime
import time"""
import glob
import logging
import os
import random
import sys
import time
from queue import Queue
from datetime import datetime
import json
import errno
try:
    sys.path.append(glob.glob('../carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

from carla import Transform, Location, Rotation
from carla import BoundingBox, Vector3D, Color
from carla import Image

# source: https://github.com/carla-simulator/scenario_runner/blob/master/scenario_runner.py
# spurce: https://github.com/carla-simulator/carla/blob/master/PythonAPI/examples/synchronous_mode.py
# source: https://github.com/carla-simulator/carla/blob/master/Docs/configuring_the_simulation.md
# source: (create directory): https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory
# source: (datetime doc): https://docs.python.org/3/library/datetime.html


class CustomVehicleManager(object):
    def __init__(self, client):
        self.client = client

        self.vehicle_lst = []
        self.vehicle_lst_id = []
        self.camera_lst = []
        self.img_queue = []

        self.debug = None
        self.settings = None
        self.frame = None

        self.parent_file_path = os.path.join('res/files/', '{}/'.format(datetime.now().date().strftime('%d_%m_%y')))
        self.parent_img_path = os.path.join('res/screenshots/', '{}/'.format(datetime.now().date().strftime('%d_%m_%y')))

        self.debug_file_dict = {'frame_id': 0, 'img_name': 'no name', 'debug_info': []}

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
            self.vehicle_lst_id.append(vehicle.id)
            print("id ", vehicle.id, " added")
            if _ == (tmp_var - 1):
                print("trying to attatch sensor to the last vehicle: ", _)
                self.on_attach_senor_to_vehicle(vehicle)
        print("end of methode spawn for vehicles")
        world.wait_for_tick()

    def on_attach_senor_to_vehicle(self, vehicle, sensor_type='sensor.camera.rgb'):
        world = self.client.get_world()
        bp = world.get_blueprint_library()
        sensor_bp = bp.find(sensor_type)
        sensor_bp.set_attribute('image_size_x', '680')
        sensor_bp.set_attribute('image_size_y', '600')
        sensor_bp.set_attribute('fov', '110')
        sensor_bp.set_attribute('sensor_tick', '3.0')
        loc = Location(x=-15.5, y=0.0, z=10.8)
        rot = Rotation(pitch=-15, yaw=10)

        transform = Transform(loc, rot)
        sensor = world.spawn_actor(sensor_bp, transform, attach_to=vehicle)
        self.camera_lst.append(sensor)
        print("sensor appended..", sensor)
        # put sensor data in the queue
        queue = Queue()

        print("starting listening")
        self.camera_lst[0].listen(queue.put)
        self.img_queue.append(queue)

    def on_debug_vehicle(self, world, world_snapshot, frame_id):
        self.debug = world.debug
        img = self.img_queue[0].get()
        print("IMG get from queue: ", img)

        if img.frame: # to get the desired picture's name in the json file
            print("same frame as the tick frame")
            self.debug_file_dict['frame_id'] = img.frame
            self.debug_file_dict['img_name'] = 'img_{}.png'.format(img.frame)
            debug_info_lst = []
            # get actor list
            actor_lst = world.get_actors(self.vehicle_lst_id)
            # retrieve object in the world snapshot through it id
            for retrieved_actor in actor_lst:
                actor_snapshot = world_snapshot.find(retrieved_actor.id)

                if retrieved_actor.is_alive:
                    transform = actor_snapshot.get_transform()
                    location = transform.location
                    rotation = transform.rotation
                    box = retrieved_actor.bounding_box
                    # extent_z = 0.5
                    # actor_id = retrieved_actor.id

                    self.draw_3d_box_and_id(location, rotation, box, retrieved_actor, debug_info_lst)

                # write the result in file and save picture
                img.save_to_disk(os.path.join(self.parent_img_path, 'img_{}'.format(img.frame)))
                print("Img created: ", img)
                self.debug_file_dict['debug_info'] = debug_info_lst
                self.write_info_in_json_file(self.debug_file_dict, img.frame)

                print("img saved! (^ ^)")
            print("returning snapshot.....")
        return world_snapshot

    def draw_3d_box_and_id(self, location, rotation, box, actor, debug_lst):
        ########## Draw 3D Box ###########
        box.extent.z += 0.7
        self.debug.draw_box(
            box=BoundingBox(
                location,
                Vector3D(
                    x=box.extent.x,
                    y=box.extent.y,
                    z=box.extent.z
                )
            ),
            rotation=rotation,
            thickness=0.13,
            color=Color(255, 10, 5),
            life_time=0.0001
        )

        ####### Draw ID as string #####
        string_position = location
        string_position.z += 2.2
        self.debug.draw_string(
            location=string_position,
            text="Id: {}".format(actor.id),
            draw_shadow=False,
            color=Color(254, 254, 254)
        )

        # add or update info in the dictionnary
        self.on_update_dict(actor, location, box, debug_lst)

    # update the information in the section debug-infos of the dict
    def on_update_dict(self, actor, location, actor_box, debug_lst):
        actor_box_lst = []
        loc_dict = {
            'x': location.x,
            'y': location.y,
            'z': location.z
        }
        actor_box_lst.append(loc_dict)
        ext_box_dict = {
            'x': actor_box.extent.x,
            'y': actor_box.extent.y,
            'z': actor_box.extent.z
        }
        actor_box_lst.append(ext_box_dict)

        actor_dict = {
            'actor_id': actor.id, 'actor_type': actor.type_id, 'actor_box': actor_box_lst
        }

        debug_lst.append(actor_dict)

    def write_info_in_json_file(self, debug_dict, frame_id):
        self.create_or_update_dir(self.parent_file_path)
        file_name = os.path.join(self.parent_file_path, 'file_{}.json'.format(frame_id))
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(debug_dict, indent=3, ensure_ascii=False))

    # create director if it not exists to avoid FileNotFoundError
    # only need in while creating the json file
    def create_or_update_dir(self, path):
        try:
            os.makedirs(path)
            print("director created")
        except OSError as e:
            if e.errno != errno.EEXIST:
                print("Error due to another Exception in directory: ", e.errno)
                raise

    def remove_all_vehicles(self):
        print("stopping sensor ")
        for sensor in self.camera_lst:
            sensor.stop()
            sensor.destroy()
        print("removing vehicles...")
        for actor in self.vehicle_lst:
            actor.destroy()
        print("vehicles destroyed!")
        self.vehicle_lst_id.clear()
        self.img_queue.clear()
        self.vehicle_lst.clear()
