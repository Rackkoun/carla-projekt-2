import carla

from model.vehicle_test import CustomVehicleManager
from model.walker_test import CustomPedestrianManager


def main():
    client = carla.Client('localhost', 2000)

    # provide enough waiting time to avoid RuntimeError while trying
    # while to wait connection answer from the server
    client.set_timeout(10.5)
    world = client.get_world()
    test_vehicle = CustomVehicleManager(client)
    test_walker = CustomPedestrianManager(client)

    try:
        test_vehicle.on_spawn_vehicles(10)
        # print("waiting for server answer before adding another actors")
        # world = client.get_world()
        # world.wait_for_tick()
        test_walker.on_spawn_walkers(5)
        print("get the last car")
        pos = len(test_vehicle.vehicle_lst) - 1
        last_vehicle = test_vehicle.vehicle_lst[pos]
        print("ID of the last car: ", last_vehicle.id)

        # get the list of actor
        actor_lst = test_vehicle.vehicle_lst
        while True:
            # world = client.get_world()
            print("synchronizing the simulator...")
            tick_id = world.tick()
            print("tick done!: ", tick_id)
            print("trying to debug on tick")
            world.on_tick(
                lambda world_snapshot: test_vehicle.on_debug_vehicle_list(world, world.get_snapshot(),
                                                                          actor_lst))
            print("Tick done --> saving data")
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
