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

import math
import random
import time

# Hello World mit Carla 
def main():
    actor_list = []

    # sensor liste
    sensor_lst = []
    try:
        # Zuerst ein Client-Objekt erzeugen
        client = carla.Client('localhost', 2000)

        # wichtig damit das Netzwerk nicht fuer ewig blokiert sei
        client.set_timeout(10.0)

        # Dann die Welt des erzeugten Klienten finden
        world = client.get_world()

        # zeige die Info uber die Welt
        print("Welt: ", world)
        
        # Erzeuge ein Held mit Blueprint Sensor, Auto, usw.
        blueprint_library = world.get_blueprint_library()
        print("Blueprint OK")
        
        # suche Sensor fuer Kollision in Blueprint
        col_sensor_bp = blueprint_library.find('sensor.other.collision')
        # waehle alle BMW-Auto in dem Library aus
        auto_bp = random.choice(blueprint_library.filter('vehicle.bmw.*'))

        print("Auto-Auswahl: ", auto_bp)

        # aendernbare attribute haben eine liste von werte 'recommended
        # z.B. die Farbe eines Auto. Aber die Anzahl an Reifen sind nicht aenderbar
        if auto_bp.has_attribute('color'):
            color = random.choice(auto_bp.get_attribute('color').recommended_values)
            auto_bp.set_attribute('color', color)

            print("Farbe: ", color)
        
        # um ein Objet zu spawnen man braucht seine Koordinaten
        transform = random.choice(world.get_map().get_spawn_points())
        print("Transform: ", transform)
        # welche dann mit Hilfe in einer Welt plaziert wird
        vehicle = world.spawn_actor(auto_bp, transform)
        
        # setze eine Kamera zu dem Auto
        #camera = world.spawn_actor(col_sensor_bp, relative_transform, attach_to=vehicle) 
        #camera_bp = blueprint_library.find('sensor.camera.depth')
        relative_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera = world.spawn_actor(col_sensor_bp, relative_transform, attach_to=vehicle)
        sensor_lst.append(camera)
        print('Kamera: ', camera)
        print('created %s' % camera.type_id)

        actor_list.append(vehicle)
        #sensor_lst.append(camera)
        print("Auto: ", vehicle)
        print('created %s' % vehicle.type_id)
        
        # aktiviere autonome fahrt
        vehicle.set_autopilot(True)

        # 
        cc = carla.ColorConverter.LogarithmicDepth
        camera.listen(lambda image: image.save_to_disk('_out/%06d.png' % image.frame_number, cc))

        # auto position
        v_location = vehicle.get_location()
        v_location.x += 40
        vehicle.set_location(v_location)
        print('moved vehicle to %s' % v_location)

        # kamera position
        c_location = camera.get_location()
        c_location.x += 40
        vehicle.set_location(c_location)
        print('moved Kamera to %s' % c_location)

        # 
        transform.location += carla.Location(x=40, y=-3.2)
        transform.rotation.yaw = -180.0
        for _ in range(0, 10):
            transform.location.x += 8.0

            auto_bp = random.choice(blueprint_library.filter('vehicle.bmw.*'))

            # 
            npc = world.try_spawn_actor(auto_bp, transform)
            if npc is not None:
                actor_list.append(npc)
                npc.set_autopilot()
                print('created %s' % npc.type_id)

        time.sleep(10)

    finally:

        print('destroying actors')
        for actor in actor_list:
            print(actor)
            actor.destroy()
        print('done for vehicle.')

        print('destroying camera')
        for cam in sensor_lst:
            print(cam)
            cam.destroy()
        print('done for sensors')


if __name__ == '__main__':

    main()