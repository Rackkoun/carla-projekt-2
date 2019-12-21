import carla

from model.vehicle_test import CustomVehicleManager
from model.walker_test import CustomPedestrianManager


def main():
    client = carla.Client('localhost', 2000)

    # provide enough waiting time to avoid RuntimeError while trying
    # while to wait connection answer from the server
    client.set_timeout(20.5)
    #world = client.get_world()
    test_vehicle = CustomVehicleManager(client)
    test_walker = CustomPedestrianManager(client)

    try:
        test_vehicle.on_spawn_vehicles(15)
        print("waiting for server answer before adding another actors")
        world = client.get_world()
        world.wait_for_tick()
        print("done 1")
        test_walker.on_spawn_walkers(20)
        while True:
            world = client.get_world()
            world.wait_for_tick()
    finally:
        print("Destroying actors...")
        test_vehicle.remove_all_vehicles()
        test_walker.on_remove_walkers()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print('Yop!')
