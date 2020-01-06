"""
:@authors: Zanguim K. L, Fozing Y. W., Tchana D. R.
"""
import glob
import os
import random
import logging
import sys
import json

try:
    sys.path.append(glob.glob('../carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
from carla import Transform, Location, Rotation
from carla import BoundingBox, Vector3D, Color

class CustomDataDebugger(object):

    def __init__(self, client):
        self.client = client
        self.sensor = None
        self.debug = None
        self.parent_file_path = 'gui/Files/Original/'
        self.img_width = 680
        self.img_height = 600
        self.fov = 110
        self.tick = 3.0
        world = self.client.get_world()
        self.sensor_bp = world.get_blueprint_library().filter('sensor.*')

        self.debug_file_dict = {
            'sensor_frame': 0,
            'sensor_specs': {'frame': 0, 'transform': {'location': {'x': 0.0, 'y': 0.0, 'z': 0.0}, 'rotation': {'roll': 0, 'pitch': 0, 'yaw': 0}}},
            'img_name': 'no name',
            'img_specs': {'width': self.img_width, 'height': self.img_height, 'fov': self.fov},
            'debug_info': []
        }

    def on_listen_data(self, sensor_data, actor_lst_id):
        world = self.client.get_world()
        debug_info_lst = []
        world_snapshot = world.get_snapshot()
        actor_lst = world.get_actors(actor_lst_id)
        #    # retrieve object in the world snapshot through it id
        for retrieved_actor in actor_lst:
            actor_snapshot = world_snapshot.find(retrieved_actor.id)

            if retrieved_actor.is_alive:
                transform = actor_snapshot.get_transform()
                location = transform.location
                #rotation = transform.rotation
                box = retrieved_actor.bounding_box
                # add or update info in the dictionnary
                self.on_update_dict(retrieved_actor, location, box, debug_info_lst)
        # write the result in file and save picture
        # img = Image(sensor_data)
        sensor_snap = world_snapshot.find(self.sensor.id)
        sensor_transform = sensor_snap.get_transform()
        sensor_rotation = sensor_transform.rotation
        sensor_location = sensor_transform.location
        location_dict = {'x': sensor_location.x, 'y': sensor_location.y, 'z': sensor_location.z}
        rotation_dict = {'roll': sensor_rotation.roll, 'pitch': sensor_rotation.pitch, 'yaw': sensor_rotation.yaw}
        self.debug_file_dict['sensor_specs']['transform']['location'] = location_dict
        self.debug_file_dict['sensor_specs']['transform']['rotation'] = rotation_dict
        sensor_data.save_to_disk(os.path.join(self.parent_file_path, '{}'.format(sensor_data.frame)))
        print("Img created: ", sensor_data)
        self.debug_file_dict['frame_id'] = sensor_data.frame
        self.debug_file_dict['img_name'] = '{}.png'.format(sensor_data.frame)
        self.debug_file_dict['debug_info'] = debug_info_lst
        self.write_info_in_json_file(self.debug_file_dict, sensor_data.frame)
        print("img saved! (^ ^)")
        return sensor_data

    # update the information in the section debug-infos of the dict
    def on_update_dict(self, actor, location, actor_box, debug_lst):
        actor_box_lst = {'location': {}, 'box_extent': {}}
        loc_dict = {
            'x': location.x,
            'y': location.y,
            'z': location.z
        }
        actor_box_lst['location'] = loc_dict
        ext_box_dict = {
            'x': actor_box.extent.x,
            'y': actor_box.extent.y,
            'z': actor_box.extent.z
        }
        actor_box_lst['box_extent'] = ext_box_dict

        actor_dict = {
            'actor_id': actor.id, 'actor_type': actor.type_id, 'actor_box': actor_box_lst
        }

        debug_lst.append(actor_dict)

    def write_info_in_json_file(self, debug_dict, frame_id):
        file_name = os.path.join(self.parent_file_path, '{}.json'.format(frame_id))
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(debug_dict, indent=3, ensure_ascii=False))
        print('File wrote (+ +)')

    def on_attach_senor_to_vehicle(self, vehicle, actor_lst_id, sensor_type='sensor.camera.rgb'):
        world = self.client.get_world()
        # bp = world.get_blueprint_library()
        sensor_bp = self.sensor_bp.find(sensor_type)
        sensor_bp.set_attribute('image_size_x', str(self.img_width))
        sensor_bp.set_attribute('image_size_y', str(self.img_height))
        sensor_bp.set_attribute('fov', str(self.fov))
        sensor_bp.set_attribute('sensor_tick', str(self.tick))
        loc = Location(x=-15.5, y=0.0, z=10.8)
        rot = Rotation(pitch=-15, yaw=10)
        location_dict = {'x': loc.x, 'y': loc.y, 'z': loc.z}
        rotation_dict = {'roll': rot.roll, 'pitch': rot.pitch, 'yaw': rot.yaw}
        self.debug_file_dict['sensor_specs']['transform']['location'] = location_dict
        self.debug_file_dict['sensor_specs']['transform']['rotation'] = rotation_dict

        transform = Transform(loc, rot)
        sensor = world.spawn_actor(sensor_bp, transform, attach_to=vehicle)
        self.sensor = sensor
        print("sensor appended..", sensor)
        # put sensor data in the queue
        # queue = Queue()

        print("starting listening")
        # self.camera_lst[0].listen(queue.put)
        self.sensor.listen(lambda sensor_data: self.on_listen_data(sensor_data, actor_lst_id))
        print("listen......")

    def on_debugged(self, world, world_snapshot, actor_lst_id):
        self.debug = world.debug
        #img = self.img_queue[0].get()
        #print("IMG get from queue: ", img)

        #if img.frame: # to get the desired picture's name in the json file
        #    print("same frame as the tick frame")
        #    self.debug_file_dict['frame_id'] = img.frame
        #    self.debug_file_dict['img_name'] = 'img_{}.png'.format(img.frame)
        #    debug_info_lst = []
        #    # get actor list
        actor_lst = world.get_actors(actor_lst_id)
        #    # retrieve object in the world snapshot through it id
        for retrieved_actor in actor_lst:
            actor_snapshot = world_snapshot.find(retrieved_actor.id)

            if retrieved_actor.is_alive:
                transform = actor_snapshot.get_transform()
                location = transform.location
                rotation = transform.rotation
                box = retrieved_actor.bounding_box
                #    # extent_z = 0.5
                #    # actor_id = retrieved_actor.id
                print('Actor retrieved: ', retrieved_actor)

                self.draw_3d_box_and_id(location, rotation, box, retrieved_actor)

                # write the result in file and save picture
                #img.save_to_disk(os.path.join(self.parent_img_path, 'img_{}'.format(img.frame)))
                #print("Img created: ", img)
                #self.debug_file_dict['debug_info'] = debug_info_lst
                #self.write_info_in_json_file(self.debug_file_dict, img.frame)

                #print("img saved! (^ ^)")
        print("returning snapshot.....")
        return world_snapshot

    def draw_3d_box_and_id(self, location, rotation, box, actor):
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

    def on_stopping_listening(self):
        if self.sensor is not None and self.sensor.is_listening:
            print("stopping lilstening...")
            self.sensor.stop()
            self.sensor.destroy()
            print("Sensor destroyed")
