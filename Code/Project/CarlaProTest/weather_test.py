
import glob
import os
import sys
import time

try:
    sys.path.append(glob.glob('carla_egg/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

from carla import Transform, Location, Rotation

def main():

    client_carla=carla.Client('localhost',2000)

    client_carla.set_timeout(12)

    my_world=client_carla.get_world()

    #my_world=client_carla.reload_world()

    #my_world=client_carla.load_world('Town02')


    actual_weather= (my_world.get_weather())

    print("actual weather:",actual_weather)

    alternate_weather= carla.WeatherParameters(cloudyness=0.0000,
                                               precipitation=0.000000,
                                               precipitation_deposits=0.0000,
                                               wind_intensity=0.000000,
                                               sun_azimuth_angle=80.340317,
                                               sun_altitude_angle=53.907822)

    new_weather=carla.WeatherParameters(
        cloudyness=100,
        precipitation=0.0,
        sun_altitude_angle=80.0,
    )

    #my_world.set_weather(new_weather)

    my_world.set_weather(alternate_weather)

    # while (True):
    #
    #
    #     #world_snapshot=my_world.wait_for_tick(600)
    #
    #     #my_world.tick()
    #
    #     #actor_snapshot=world_snapshot.find(new_actor.id)
    #
    #     transform = new_actor.get_transform()
    #     bounding_box = new_actor.bounding_box
    #     bounding_box.location += transform.location
    #     my_world.debug.draw_box(bounding_box, transform.rotation,life_time=0.2,persistent_lines=True)
    #
    #     time.sleep(0.2)
    #
    # # camera_bp=blueprint_library.find('sensor.camera.rgb')
    # #
    # # print(camera_bp)
    # #
    # # camera=my_world.spawn_actor(camera_bp,my_transform,attach_to=new_actor)
    # #
    # # print(camera)


if __name__=='__main__':
     main()