"""
:@authors: Zanguim K. L, Fozing Y. W., Tchana D. R.
"""
import glob
import os
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
from carla import ColorConverter


class CustomDataDebugger(object):
    """
    Class to debug all actor in the world and generate image and json files.
    All generated image and file will be save in the same folder (/gui/Files/Original/)
    and will have the same name (frame number of the generated Carla-Image).

    :param client: get the current connected client to the Carla-Server
    """

    def __init__(self, client):
        self.client = client
        world = self.client.get_world()

        self.sensor = None  # to save the actual used sensor or camera
        self.debug = None  # to activate the debugging in the current world

        self.json_path = 'res/files/json/'  # path to save generated images and json files
        self.img_semseg_path = 'res/files/semseg/'
        self.img_depth_path = 'res/files/depth/'
        self.img_rgb_path = 'res/files/rgb/'
        self.img_width = 640  # image width; suitable to change the Image resolution
        self.img_height = 680
        self.fov = 100
        self.tick = 3.0  # images and json files will be generated every 3 ticks

        self.sensor_bp = world.get_blueprint_library().filter('sensor.*')  # get all sensors (camera inclusive)

        self.debug_file_dict = {  # design the structure to save information in the json file
            'cam_type': None,  # class
            'cam_id': 0,  # ID
            'cam_location': {'x': 0.0, 'y': 0.0, 'z': 0.0},  # Position
            'cam_rotation': {'roll': 0, 'pitch': 0, 'yaw': 0},  # Rotation
            'img_name': 'no name',
            'img_width': self.img_width,
            'img_height': self.img_height,
            'img_fov': self.fov,
            'debug_info': []  # placeholder to save all information of spawned actors
        }

    def on_listen_data(self, sensor_data, actor_lst_id):
        """
        Callback-method for the 'listen-method' for Carla-Sensor. The method must take sensor data and give it back;
        Carla-Image will be created through the sensor data and then save in the disk. The information of all actors
        that are still alive in the world will be retrieved, then wrote in a json file.

        :param sensor_data: will be automatically generate through the method 'listen' of Carla-Sesnor
        :param actor_lst_id: list containing the identifier of all actors currently alive in the world
        :return: sensor_data
        """
        world = self.client.get_world()  # get the world through the connected client
        debug_info_lst = []  # list to save information of all actors in the current world
        world_snapshot = world.get_snapshot()  # get a snapshot of the world at this moment
        actor_lst = world.get_actors(actor_lst_id)  # then retrieve all actors at the given moment in the world

        for retrieved_actor in actor_lst:  # from the returned list, find each actor through its ID
            actor_snapshot = world_snapshot.find(retrieved_actor.id)

            if retrieved_actor.is_alive:  # check if the retrieved actor is still alive
                transform = actor_snapshot.get_transform()  # then get its position in the world
                location = transform.location
                box = retrieved_actor.bounding_box  # and its bounding box to write them later in the json file
                self.on_update_dict(retrieved_actor, location, box, debug_info_lst)

        # retrieve the camera to write its information in the json file too
        sensor_snap = world_snapshot.find(self.sensor.id)
        sensor_transform = sensor_snap.get_transform()
        sensor_rotation = sensor_transform.rotation
        sensor_location = sensor_transform.location
        location_dict = {'x': sensor_location.x, 'y': sensor_location.y, 'z': sensor_location.z}
        rotation_dict = {'roll': sensor_rotation.roll, 'pitch': sensor_rotation.pitch, 'yaw': sensor_rotation.yaw}
        self.debug_file_dict['cam_location'] = location_dict
        self.debug_file_dict['cam_rotation'] = rotation_dict

        # save the generated image in the disk
        semseg_convertor = ColorConverter.CityScapesPalette
        depth_convertor = ColorConverter.Depth
        # save in folder for original images
        sensor_data.save_to_disk(os.path.join(self.img_rgb_path, '{}'.format(sensor_data.frame)))
        # save in folder for semantic segmented images
        sensor_data.save_to_disk(os.path.join(self.img_semseg_path, '{}'.format(sensor_data.frame)), semseg_convertor)
        # save in folder for depth converted images
        sensor_data.save_to_disk(os.path.join(self.img_depth_path, '{}'.format(sensor_data.frame)), depth_convertor)
        print("Img created: ", sensor_data)

        # update the dictionary's information
        self.debug_file_dict['cam_type'] = self.sensor.type_id
        self.debug_file_dict['cam_id'] = self.sensor.id
        self.debug_file_dict['img_name'] = '{}.png'.format(sensor_data.frame)
        self.debug_file_dict['debug_info'] = debug_info_lst

        # and then convert the dictionary in json-format and save it in the disk too
        self.write_info_in_json_file(self.debug_file_dict, sensor_data.frame)
        print("img saved! (^ ^)")
        return sensor_data

    # update the information in the section debug-info of the dict
    def on_update_dict(self, actor, location, actor_box, debug_lst):
        # current location of the actor in the world snapshot
        actor_location_dict = {
            'x': location.x,
            'y': location.y,
            'z': location.z
        }
        # 3D BBOX
        bbox_3d_dict = {
            'xpos': actor_box.extent.x,
            'ypos': actor_box.extent.y,
            'zpos': actor_box.extent.z
        }
        # 2D BBOX
        bbox_2d_dict = {
            'xmin': 0.0,
            'ymin': 0.0,
            'xmax': actor_box.extent.x,
            'ymax': actor_box.extent.y
        }
        # actor_box_lst['box_extent'] = ext_box_dict

        actor_dict = {
            'actor_type': actor.type_id,
            'actor_id': actor.id,
            'actor_location': actor_location_dict,
            'actor_bbox_2d': bbox_2d_dict,
            'actor_bbox_3d': bbox_3d_dict
        }

        debug_lst.append(actor_dict)

    # Method to convert a python-dict in json-format and then write it in the disk
    def write_info_in_json_file(self, debug_dict, frame_id):
        file_name = os.path.join(self.json_path, '{}.json'.format(frame_id))
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(json.dumps(debug_dict, indent=3, ensure_ascii=False))
        print('File wrote (+ +)')

    def on_attach_senor_to_vehicle(self, vehicle, actor_lst_id, sensor_type='sensor.camera.rgb'):
        """
        Attaching a sensor to an actor (e.g: vehicle) need to get the list of all actor's ID (see @method on_listen_data)

        :param vehicle: actor to that the selected sensor will be attached as child
        :param actor_lst_id: list of all actor's ID in the world
        :param sensor_type: selected sensor
        :return:
        """
        world = self.client.get_world()
        sensor_bp = self.config_camera(sensor_type)  # configure the camera blueprint

        loc = Location(x=-5.5, y=0.0, z=1.8)
        rot = Rotation(roll=0, pitch=0, yaw=0)
        location_dict = {'x': loc.x, 'y': loc.y, 'z': loc.z}
        rotation_dict = {'roll': rot.roll, 'pitch': rot.pitch, 'yaw': rot.yaw}
        self.debug_file_dict['cam_location'] = location_dict
        self.debug_file_dict['cam_rotation'] = rotation_dict

        transform = Transform(loc, rot)
        print('appending camera to the last vehicle...')
        self.sensor = world.spawn_actor(sensor_bp, transform, attach_to=vehicle)  # spawn the sensor in the world
        print("sensor appended..", self.sensor)

        print("starting listening")  # then start to listen data
        self.sensor.listen(lambda sensor_data: self.on_listen_data(sensor_data, actor_lst_id))
        print("listen......")

    def on_debugged(self, world, world_snapshot, actor_lst_id):
        """
        Debugging the world will be done on every tick. A Snapshot of the world is needed for the callback method 'on_tick'
        :param world:
        :param world_snapshot: this parameter must be give as parameter and then returned too
        :param actor_lst_id:
        :return:
        """
        self.debug = world.debug  # activate the debugging
        actor_lst = world.get_actors(actor_lst_id)  # get the list of all actors in the world

        for retrieved_actor in actor_lst:  # for each retrieved actor
            actor_snapshot = world_snapshot.find(retrieved_actor.id)

            if retrieved_actor.is_alive:  # get its position if it is still alive
                transform = actor_snapshot.get_transform()
                location = transform.location
                rotation = transform.rotation
                box = retrieved_actor.bounding_box
                print('Actor retrieved: ', retrieved_actor)
                print("############## trying to drow Box ###############")
                # self.draw_3d_box_and_id(location, rotation, box, retrieved_actor)  # then draw the bounding box

        print("returning snapshot.....")
        return world_snapshot

    # Method for drawing bounding box
    def draw_3d_box_and_id(self, location, rotation, box, actor):
        # ######### Draw 3D Box ###########
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

        # ###### Draw ID as string #####
        string_position = location
        string_position.z += 2.2
        self.debug.draw_string(
            location=string_position,
            text="Id: {}".format(actor.id),
            draw_shadow=False,
            color=Color(254, 254, 254)
        )

    def config_camera(self, cam_type):
        sensor_bp = self.sensor_bp.find(cam_type)  # find the selected sensor in the library
        # set the sensor attributes
        sensor_bp.set_attribute('image_size_x', str(self.img_width))
        sensor_bp.set_attribute('image_size_y', str(self.img_height))
        sensor_bp.set_attribute('fov', str(self.fov))
        sensor_bp.set_attribute('sensor_tick', str(self.tick))
        return sensor_bp

    # Method to destroy all living actors in the current world
    def on_stopping_listening(self):
        print("stopping listening and destroying camera...")
        if self.sensor is not None and self.sensor.is_listening:
            self.sensor.stop()
            self.sensor.destroy()
        print("Done!")
