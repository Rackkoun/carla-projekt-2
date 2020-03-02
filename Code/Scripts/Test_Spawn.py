
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

    #my_world=client_carla.load_world('Town05')

    blueprint_library=my_world.get_blueprint_library()

    #print("blueprint_library=",blueprint_library)

    autos=blueprint_library.filter('vehicle.*')

    # for x in autos:
    #     print("auto=",x)

    bikes=[]

    cars=[]

    ## we select only vehicles with 2 wheels
    for x in autos:
        if int(x.get_attribute('number_of_wheels'))==2:
            bikes.append(x)
        if int(x.get_attribute('number_of_wheels'))==4:
            cars.append(x)

    print("Number of bike=",len(bikes),"number of car=",len(cars))

    i=0
    for x in bikes:
        if x.has_attribute('color'):
            x.set_attribute('color','255,0,204')
            i=i+i
    print("Number of changed bikes color=",i)

    i=0
    for x in cars:
        if x.has_attribute('color'):
            x.set_attribute('color','0,0,255')
            i=i+1
    print("Number of changed cars color=",i)

    spawn_points=my_world.get_map().get_spawn_points()

    #spawn_points=[]

    transform=carla.Transform()
    transform.location.x=17578.751953
    transform.location.y=2666.687500
    transform.location.z=27.327530

    transform.location.x=20
    transform.location.y=20
    transform.location.z=27.327530

    #spawn_points = carla.Transform((X=17578.751953,Y=22666.687500,Z=27.327530))
    #(Pitch=-0.000031, Yaw=-0.000061, Roll=0.000000)

    transform.rotation.pitch=-0.000031
    transform.rotation.yaw=0.000061
    transform.rotation.roll=0.000000

    transform=Transform(Location(x=176.300751, y=225.862961, z=0.285932), Rotation(pitch=-0.037839, yaw=3.241943, roll=-0.000214))

    print("transform:",transform)

    #spawn_points.append(transform)

    for x in spawn_points:
        #print("Spawn points:",x)
        pass

    my_car=cars[0]

    #my_transform=spawn_points[0]

    #new_actor=my_world.spawn_actor(my_car,my_transform)





    #new_actor = my_world.try_spawn_actor(my_car, transform)


    #new_actor = my_world.try_spawn_actor(my_car, spawn_points[2])

    new_actor =None

    #new_actor.set_autopilot()


    if new_actor is not None:
        #new_actor.set_autopilot()
        print('new actor:',  new_actor.type_id)


    if(new_actor is None):
        print("could not spawn actor")

    print("new actor transform:",new_actor.get_transform())

    # new_actor.set_transform(transform)
    #
    # print("new actor transform:", new_actor.get_transform())

    # settings = my_world.get_settings()
    # settings.synchronous_mode = True
    # my_world.apply_settings(settings)

    print("number of actor:",len(my_world.get_actors()))
    print("########all actors locations########")
    for actor in my_world.get_actors():
        if actor.attributes.get('role_name') == 'hero':
            print("hero transform:",actor.get_transform())
            pass

    #camera_bp=blueprint_library.find('sensor.camera.rgb')

    new_weather=carla.WeatherParameters(
        cloudyness=10.0,
        precipitation=30.0,
        sun_altitude_angle=70.0
    )

    my_world.set_weather(new_weather)

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