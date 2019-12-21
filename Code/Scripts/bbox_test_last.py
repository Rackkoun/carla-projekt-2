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
import time
from datetime import datetime
import numpy as np

import json

obj_lst = []
IMG_WIDTH =640
IMG_HEIGHT = 480

PATH = './Code/File/'


#

def create_auto(world, pos=0):
    blueprint = random.choice(world.get_blueprint_library().filter('mercedes-benz.*'))
    blueprint.set_attribute('color', '255,0,0')

    transform =  world.get_map().get_spawn_points()[pos]

    mustang = world.spawn_actor(blueprint, transform)
    mustang.set_autopilot()
    world.wait_for_tick()

    return mustang

def createSensor(world, vehicle):
    blueprint = world.get_blueprint_library().find('sensor.camera')
    blueprint.set_attribute('post_processing', 'SceneFinal')
    camera = world.spawn_actor(
        blueprint,
        carla.Transform(carla.Location(x=0.5, z=1.8)),
        attach_to=vehicle)
    return camera

def wetter_einstellen(welt, sonne_orientierung, wolkigkeit, regen_rate):
    wetter = carla.WeatherParameters(
        sun_altitude_angle=sonne_orientierung,
        cloudyness=wolkigkeit,
        precipitation=regen_rate
    )
    welt.set_weather(wetter)
    print("Wetter: ", wetter)

if __name__=="__main__":
    client = carla.Client('localhost', 2000)
    client.set_timeout(2.0) 
    world = client.get_world()
    #blueprint_library = world.get_blueprint_library()
    print("WORLD: ", world)
    
    wetter_einstellen(world, 80.0, 1.0, 5.0)
    m_auto = create_auto(world=world)
    sensor = createSensor(world, m_auto)
    sensor.listen(lambda img: img.save_to_disk('bilder/autos/test01/%04d.png'% img.frame))

    time.sleep(6)
    if m_auto.is_alive:
        print("Actor is still alive stop sensor listening")
        if sensor.is_listening is True:
            print("Sensor still listen to data")
            sensor.stop()
            print("Sesnor stopped")
        m_auto.destroy()
        print("actor is killed")
    