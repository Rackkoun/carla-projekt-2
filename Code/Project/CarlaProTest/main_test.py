"""
:@authors: Zanguim K. L, Fozing Y. W., Tchana D. R.
"""
import glob
import os
import sys

try:
    sys.path.append(glob.glob('carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass
import carla
from carla import WeatherParameters
from model.vehicle_test import CustomVehicleManager
from model.walker_test import CustomPedestrianManager
from model.sensor_test import CustomDataDebugger


# provide enough waiting time to avoid RuntimeError while trying
# while to wait connection answer from the server
def on_setting_world(client, desired_map='Town02'):
    # retrieve the world through the current client
    world = client.load_world(desired_map)

    settings = world.get_settings()
    weather = WeatherParameters(
        cloudyness=1.0,
        precipitation=0.0,
        sun_altitude_angle=88.7)
    world.set_weather(weather)
    world.apply_settings(settings)

    # client.reload_world()
    print('World setting done!')
    #
    # # world = client.get_world()
    # # current_map = world.get_map()
    #
    # # loading the world cause an runtime-exception at the first time
    # # that the program ist launched
    # if current_map.name is not desired_map:
    #     try:
    #         # get the world settings and check if synchronized_mode is enable
    #         # client.reload_world()
    #
    #
    #         print("Desired Map's name: ", desired_map)
    #     except RuntimeError as error:
    #         print("Error while changing the town: ", error)

    return world


def main():
    client = carla.Client('localhost', 2000)  # create a client
    client.set_timeout(10.5)  # set Server-Polling to 10.5 second
    world = on_setting_world(client)

    # Create vehicles, Walkers and a camera
    test_vehicle = CustomVehicleManager(client)
    test_walker = CustomPedestrianManager(client)
    test_sensor = CustomDataDebugger(client)
    actor_id = []
    try:
        # Spawn vehicles and walkers
        test_vehicle.on_spawn_vehicles(15)
        print("waiting for server answer before adding another actors")
        test_walker.on_spawn_walkers(30)

        # retrieve the last spawned vehicle through its position in the vehicle list (class CustomVehicleManager)
        pos = len(test_vehicle.vehicle_lst) - 1
        last_vehicle = test_vehicle.vehicle_lst[pos]
        print("ID of the last car: ", last_vehicle.id)

        # save all actor_id in the same list
        for vehicle in test_vehicle.vehicle_lst:
            actor_id.append(vehicle.id)

        for walker in test_walker.walker_lst:
            actor_id.append(walker.id)

        # attach the camera to last vehicle and the list of all actor's ID
        print("Number of actors saved in the list: ", len(actor_id))
        test_sensor.on_attach_senor_to_vehicle(last_vehicle, actor_id)  # that method enable the sensor listening

        while True:
            world = client.get_world()
            tick_id = world.tick()
            print("tick done!: ", tick_id)  # debug the world in every tick drawing boxes for all actors
            world.on_tick(lambda world_snapshot: test_sensor.on_debugged(world, world_snapshot, actor_id))
            print("end of while")

    finally:
        print("Destroying actors...")
        test_sensor.on_stopping_listening()
        test_walker.on_remove_walkers()
        test_vehicle.remove_all_vehicles()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('Yop!')
