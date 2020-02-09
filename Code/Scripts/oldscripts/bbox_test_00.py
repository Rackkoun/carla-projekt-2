""" 
    1- Draw box around object
    2- Make a segmentation of object in the view
"""

import glob
import os
import sys

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import random
import logging

sensor_auto_lst = []
autos_lst = []
pedest_lst = []

def obj_in_box():
    try:
        klient = carla.Client('localhost', 2000)
        klient.set_timeout(3.5)
        welt = klient.get_world()

        # debug for drawing box
        w_debug = welt.debug
        print("Debug: ", w_debug)
        
        #zuschauer = welt.get_spectator()
        # Special for walker we have to create a walker
        # then set a controller for the created walker: carla 9.6
        # get library
        # source: http://carla.org/2019/07/12/release-0.9.6/
        kamera_lib = welt.get_blueprint_library().find('sensor.camera.rgb')
        kamera_lib.set_attribute('image_size_x', str(500))
        kamera_lib.set_attribute('image_size_y', str(500))

        andere_kamera_lib = welt.get_blueprint_library().find('sensor.camera.semantic_segmentation')
        andere_kamera_lib.set_attribute('image_size_x', str(500))
        andere_kamera_lib.set_attribute('image_size_y', str(500))

        auto_lib = welt.get_blueprint_library().filter('vehicle.mercedes-benz.*')
        laeufer_lib = welt.get_blueprint_library().filter('walker.*')
        laeufer_controller_lib = welt.get_blueprint_library().find('controller.ai.walker')

        # Transform
        auto_transform_00 = welt.get_map().get_spawn_points()[0]
        laeufer_transform_00 = welt.get_map().get_spawn_points()[2]
        kamera_transform = carla.Transform(carla.Location(x=1.8, y=1.2, z=1.7))

        # Create Actors
        auto_bp = random.choice(auto_lib)
        mercedes_benz = welt.spawn_actor(auto_bp, auto_transform_00)
        welt.tick()
        mercedes_benz.set_autopilot(True)
        print('Autopilot enabled')

        kamera_auto = welt.spawn_actor(kamera_lib, kamera_transform, attach_to=mercedes_benz)
        welt.wait_for_tick()
        print("Camera attached to actors: auto")

        auto_actor_00 = welt.get_actor(mercedes_benz.id)
        print("WW: ", auto_actor_00)
        actor_00 = welt.get_actor(auto_actor_00.id)
        """ print("Trans: {}, Vel: {}, acc: {}, Actor 1: {}".format(
            auto_actor_00.get_transform(),
            auto_actor_00.get_velocity(),
            auto_actor_00.get_acceleration(),
            actor_00
        )) """
        ########################################
        # box for auto
        ########################################
        w_debug.draw_box(
            carla.BoundingBox(
                auto_actor_00.get_transform().location,
                carla.Vector3D(5.5, 5.5, 5.5)
            ),
            auto_actor_00.get_transform().rotation,
            0.05,
            carla.Color(255, 120, 0, 0),
            1
        )
        print("Debug 1:\n", w_debug)

        laeufer_bp = random.choice(laeufer_lib)
        laeufer = welt.spawn_actor(laeufer_bp, laeufer_transform_00)
        welt.tick()

        laeufer_ai = welt.spawn_actor(laeufer_controller_lib, carla.Transform(), laeufer)
        welt.tick()

        kamera_laeufer = welt.spawn_actor(andere_kamera_lib, kamera_transform, attach_to=laeufer_ai)
        welt.tick()

        print("Camera attached to actors: laeufer")
        print("Laeufer: ", laeufer, "\nLaeufer AI: ", laeufer_ai)
        laeufer_actor_00 = welt.get_actor(laeufer_ai.id)
        actor_01 = welt.get_actor(laeufer_actor_00.id)
        """ print("Trans: {}, Vel: {}, acc: {}, Actor 2: {}".format(
            laeufer_actor_00.get_transform(),
            laeufer_actor_00.get_velocity(),
            laeufer_actor_00.get_acceleration(),
            actor_01
        )) """
        #########################################
        # box pedestrian
        #########################################
        w_debug.draw_box(
            carla.BoundingBox(
                laeufer_actor_00.get_transform().location,
                carla.Vector3D(2.5, 2.5, 2.5)
            ),
            laeufer_actor_00.get_transform().rotation,
            0.05,
            carla.Color(255, 120, 0, 0),
            1
        )
        print("Debug 2:\n", w_debug)
        laeufer_ai.start()
        print('Laeufer start enable enabled')
        laeufer_ai.go_to_location(welt.get_random_location_from_navigation())
        laeufer_ai.set_max_speed(random.random() + 1)
        
        welt.tick()
        #zuschauer.set_transform(auto_snapshot.get_transform())

        
        mbox = mercedes_benz.bounding_box
        lbox = laeufer.bounding_box
        
        print(#"Zusha:\n", zuschauer,
              #"\nWelt snap:\n", auto_actor_00,
              #"\nAuto Snap:\n", auto_snapshot,
              "\nKam actor 1:\n", kamera_auto,
              "\nAuto BBox: ", mbox,
              "\nBox Loc: ", mbox.location,
              "\nBox extend: ", mbox.extent,
              "\nKam actor 2:\n", kamera_laeufer,
              "\nAuto BBox: ", lbox,
              "\nBox Loc: ", lbox.location,
              "\nBox extend: ", lbox.extent)
        kamera_auto.listen(lambda img: img.save_to_disk('bilder/autos/%04d.png'% img.frame))
        img_converter = carla.ColorConverter.CityScapesPalette
        kamera_laeufer.listen(lambda img: img.save_to_disk('bilder/personen/%04d.png'% img.frame, img_converter))
        while True:
            welt.wait_for_tick()

    finally:
        print("destroying actors")
        kamera_auto.stop() # stop listening the data
        kamera_auto.destroy()
        mercedes_benz.destroy()
        
        print("Autos successfully destroyed\n")

        print("Stopping walker process...\n")
        laeufer_ai.stop()
        kamera_laeufer.stop()
        kamera_laeufer.destroy()
        laeufer.destroy()
        laeufer_ai.destroy()
        
        print('walkers successfully destroyed\n')
        print("\nDone!")

if __name__=='__main__':
    try:
        obj_in_box()
    except KeyboardInterrupt:
        pass
    finally:
        print("All is done!")