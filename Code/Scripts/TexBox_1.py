
import glob
import os
import sys
import time

try:
    sys.path.append(glob.glob('../../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla

def main():

    client_carla=carla.Client('localhost',2000)

    client_carla.set_timeout(12)

    #my_world=client_carla.get_world()

    #my_world=client_carla.reload_world()

    my_world=client_carla.load_world('Town02')

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

    # for x in spawn_points:
    #      print("Spawn points:",x)

    my_car=cars[5]

    #my_transform=spawn_points[0]

    #new_actor=my_world.spawn_actor(my_car,my_transform)



    for transform in spawn_points:
        new_actor = my_world.try_spawn_actor(my_car, transform)
        if new_actor is not None:
            new_actor.set_autopilot()
            print('new actor:',  new_actor.type_id)
            break

    if(new_actor is None):
        print("could not spawn actor")

    # settings = my_world.get_settings()
    # settings.synchronous_mode = True
    # my_world.apply_settings(settings)

    #camera_bp=blueprint_library.find('sensor.camera.rgb')

    new_weather=carla.WeatherParameters(
        cloudyness=10.0,
        precipitation=30.0,
        sun_altitude_angle=70.0
    )

    my_world.set_weather(new_weather)

    while (True):


        #world_snapshot=my_world.wait_for_tick(600)

        #my_world.tick()

        #actor_snapshot=world_snapshot.find(new_actor.id)

        transform = new_actor.get_transform()
        bounding_box = new_actor.bounding_box
        bounding_box.location += transform.location
        my_world.debug.draw_box_red(bounding_box, transform.rotation, life_time=0.2, persistent_lines=True)

        time.sleep(0.2)

    # camera_bp=blueprint_library.find('sensor.camera.rgb')
    #
    # print(camera_bp)
    #
    # camera=my_world.spawn_actor(camera_bp,my_transform,attach_to=new_actor)
    #
    # print(camera)


if __name__=='__main__':
     main()