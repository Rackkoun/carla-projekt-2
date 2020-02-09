#!/usr/bin/env python

# Copyright (c) 2019 Computer Vision Center (CVC) at the Universitat Autonoma de
# Barcelona (UAB).
#
# This work is licensed under the terms of the MIT license.
# For a copy, see <https://opensource.org/licenses/MIT>.


############################
# Skript fuer Laeufer      #
# Modified by: Leforestier #
############################

"""Spawn NPCs into the simulation"""

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

import argparse
import logging
import random


def main():
    customparser = argparse.ArgumentParser(
        description=__doc__)
    customparser.add_argument(
        '--host',
        metavar='H',
        default='127.0.0.1',
        help='IP of the host server (default: 127.0.0.1)')
    customparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    customparser.add_argument(
        '-n', '--number-of-vehicles',
        metavar='N',
        default=10,
        type=int,
        help='number of vehicles (default: 10)')
    customparser.add_argument(
        '-d', '--delay',
        metavar='D',
        default=2.0,
        type=float,
        help='delay in seconds between spawns (default: 2.0)')
    customparser.add_argument(
        '--safe',
        action='store_true',
        help='avoid spawning vehicles prone to accidents')

    # custom option for bounding-box here
    args = customparser.parse_args()

    logging.basicConfig(
        format='%(levelname)s: %(message)s', level=logging.INFO)

    # erzeuge eine leere Liste
    walker_lst = []
    tmp_lst = []
    walkers = []
    
    # erzeuge eine Klient-Instanz von Carla
    client = carla.Client(args.host, args.port)

    # setzte ein Timer fuer das Netzwerk
    client.set_timeout(2.5)

    try:
        # hole eine Welt
        world = client.get_world()

        # hole Laeufer in der Library and waehle eins aus
        blueprints_walkers = world.get_blueprint_library().filter('walker.pedestrian.*')
        w_bp = random.choice(blueprints_walkers)

        # hole alle zufaellige Position um ein Aktor zu erzeugen
        # z.B.: 10
        points = []
        for i in range(10):
            sp = carla.Transform()
            pos = world.get_random_location_from_navigation()
            if (pos != None):
                sp.location = pos
                points.append(sp)
        
        # erzeuge ein Batch um die Laeufer zu multiplizieren
        batch = []
        for i in points:
            w_bp = random.choice(blueprints_walkers)

            # set Laufer als 'not invincible'
            if w_bp.has_attribute('is_invincible'):
                w_bp.set_attribute('is_invincible', 'false')
            batch.append(carla.command.SpawnActor(w_bp, i))
        for b in range(len(batch)):
            print("BATCH --> \n", batch[b])
        
        res = client.apply_batch_sync(batch, True)
        for i in range(len(res)):
            if res[i].error:
                logging.error(res[i].error)
            else:
                walker_lst.append({"id": res[i].actor_id})
        
        # erzeuge ein Kontroller
        batch = []
        wc_bp = world.get_blueprint_library().find('controller.ai.walker')
        for i in range(len(walker_lst)):
            batch.append(carla.command.SpawnActor(wc_bp, carla.Transform(), walker_lst[i]['id']))
        
        res = client.apply_batch_sync(batch, True)
        for i in range(len(res)):
            if res[i].error:
                logging.error(res[i].error)
            else:
                walker_lst[i]['con'] = res[i].actor_id
        
        # setze alle Laeufer in derselben Liste zusammen
        for i in range(len(walker_lst)):
            tmp_lst.append(walker_lst[i]['con'])
            tmp_lst.append(walker_lst[i]['id'])
        walkers = world.get_actors(tmp_lst)

        # kleine Wartezeit
        world.wait_for_tick()

        # initializiere jeder Kontroller
        for i in range(0, len(tmp_lst), 2):
            # starte Laeufer
            walkers[i].start()
            walkers[i].go_to_location(world.get_random_location_from_navigation())
            walkers[i].set_max_speed(1 + random.random())
        
        # lange warten
        while True:
            world.wait_for_tick()

    finally:
        print("Alle Laeufer stoppen...")
        for i in range(0, len(tmp_lst), 2):
            walkers[i].stop()
        
        print("Zerstoerung der Laeufer...")
        client.apply_batch([carla.command.DestroyActor(x) for x in tmp_lst])
        print("Destrution OK!")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("\nDone!")
