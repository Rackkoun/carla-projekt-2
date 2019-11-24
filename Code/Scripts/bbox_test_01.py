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

start_time = time.time()

carla_obj = {}
carla_obj['carla_object'] = []
carla_obj_vehicle = {
    "id":0,
    "type":"",
    'debug_infos':[]
    }
vehicle_debug_infos = {}

def debug_to_json_file(debug_inf, f_name):
    file_name = os.path.join(PATH,"{}_{}.json".format(f_name, datetime.now()))
    with open(file_name, "w", encoding='utf-8') as f:
        f.write(json.dumps(debug_inf, indent=3, ensure_ascii=False))

# 1- erzeuge eine Klient-Instanz und gebe ihm zurueck samt ihrer Welt
def initialisiere_klient_instanz():
    klient = carla.Client('localhost', 2000)
    klient.set_timeout(4.5)
    welt = klient.get_world()
    return klient, welt, welt.get_blueprint_library()

# 2- fuege Objekt in der Welt hinzu
# --> Auto
def fuege_neues_auto_hinzu(welt, bp_lib, obj_location_int, obj_class='vehicle', obj_verfeinern=None):
    neues_obj = None
    neues_obj_snapshot = None

    if obj_verfeinern is None:
        obj_verfeinern = str('*')
        obj_bp = random.choice(bp_lib.filter(obj_class + str('.') + obj_verfeinern))
        obj_pos = welt.get_map().get_spawn_points()[obj_location_int]
        neues_obj = welt.spawn_actor(obj_bp, obj_pos)
        neues_obj_snapshot = welt.get_snapshot()
        welt.tick()
        print("Objekt hinzugefuegt")
    else:
        obj_bp = random.choice(bp_lib.filter(obj_class + str('.') + obj_verfeinern))
        obj_pos = welt.get_map().get_spawn_points()[obj_location_int]
        neues_obj = welt.spawn_actor(obj_bp, obj_pos)
        neues_obj_snapshot = welt.get_snapshot()
        welt.wait_for_tick()
        print("Objekt hinzugefuegt")

    return neues_obj, neues_obj_snapshot

# --> Sensor
def fuege_neuer_sensor_hinzu(welt, bp_lib, verbundene_obj, loc_x=1.5, loc_y=0.0, loc_z=0.8):
    sensor_tranform = carla.Transform(carla.Location(x=loc_x, y=loc_y, z=loc_z))

    sensor = welt.spawn_actor(bp_lib, sensor_tranform, attach_to=verbundene_obj)
    sensor_snapshot = welt.get_snapshot()
    #welt.tick()
    welt.wait_for_tick()

    return sensor, sensor_snapshot
# 3- stelle Objekt-Verhalten ein
# --> Auto
def auto_verhalten_einstellen(auto_obj, geschindigkeit, steuerung):
    auto_obj.apply_control(carla.VehicleControl(throttle=geschindigkeit,
                                                steer=steuerung))
    print("Autoeinstellingen aktualisiert!")

# --> Sensor
def sensor_bilder_einnahme_einstellen(sensor_lib, bild_breite=IMG_WIDTH,
                        bild_groesse=IMG_HEIGHT,bild_perspektiv=110):
    sensor_lib.set_attribute('image_size_x', str(bild_breite))
    sensor_lib.set_attribute('image_size_y', str(bild_groesse))
    sensor_lib.set_attribute('fov', str(bild_perspektiv))
    print("Sensoreinstellungen aktualisiert!")

def process_img(img):
    img.save_to_disk('bilder/autos/test01/%04d.png'% img.frame)

def obj_daten_debuggen(auto_obj):
    print("Acc: {}, Vel: {}, Loc: {}".format(auto_obj.get_acceleration(), auto_obj.get_velocity(), auto_obj.get_location()))
    box = auto_obj.bounding_box
    print("Location Box: {}, Extent: {}".format(box.location, box.extent))

# Helligkeit der Simulatorsicht steuern (Wetter)
def wetter_einstellen(welt, sonne_orientierung, wolkigkeit, regen_rate):
    wetter = carla.WeatherParameters(
        sun_altitude_angle=sonne_orientierung,
        cloudyness=wolkigkeit,
        precipitation=regen_rate
    )
    welt.set_weather(wetter)
    print("Wetter: ", wetter)
# Waypoint testen
def weg_in_der_stadt_debuggen(welt, auto_obj, wege_projetieren=False, projektion_type=None):
    map = welt.get_map()
    print("NAME der STADT: ", map.name)
    wege_spur = map.get_waypoint(
        auto_obj.get_location(),
        project_to_road=wege_projetieren,
        lane_type=projektion_type
        )
    auto_obj.set_transform(wege_spur.transform)

def welt_einstellen(klient, welt, kamera, neue_welt='Town03', synchr=True):
    # welt aendern: world = client.load_world('Town01') --> world = client.reload_world()
    # synchronisieren
    einstellungen = welt.get_settings()
    einstellungen.synchronous_mode = synchr
    welt.apply_settings(einstellungen)

# suche ein Objekt in der Welt
def on_debugging(obj_snap, welt, obj):
    debug = welt.debug
    if obj.is_alive:
        print("Actor is stil alive...")
        print("retrieve actor snap")
        act_snap = obj_snap.find(obj.id)
        print("retrieve actor in the world")
        act = welt.get_actor(act_snap.id)

        print("Actor\n", act)
        print("ID: ", act.id)
        print("type: ", act.type_id)
        print("drawing debug...")

        carla_obj_vehicle['id'] = act.id
        carla_obj_vehicle['type'] = act.type_id
        #w_id = welt.tick()
        # saving location and extend in tmp var
        aloc = act.get_location()
        bbox = act.bounding_box
        
        xx = (aloc.x + bbox.location.x) /2.5
        yx = bbox.extent.y # * 0. mit null multiplizieren, um ein Viereck zu haben
        zx = bbox.extent.z + 0.7

        debug.draw_box(
            box=carla.BoundingBox(
                aloc,
                carla.Vector3D(
                    x=xx,
                    y=yx,
                    z=zx
                )
            ),
            rotation=act.get_transform().rotation,
            thickness=0.16,
            color=carla.Color(250, 10,10),
            life_time=0.001
        )
        # draw id
        sloc = aloc
        sloc.z += 2.2 
        debug.draw_string(
            location=sloc,
            text="Id: {}".format(act_snap.id),
            draw_shadow=False,
            color=carla.Color(250, 255, 255)
            #life_time=0.01
        )

        vehicle_debug_infos['location'] = {
            'x':act.get_location().x,
            'y':act.get_location().y,
            'z':act.get_location().z
        }
        vehicle_debug_infos['extent'] = {
            'x':act.bounding_box.extent.x,
            'y':act.bounding_box.extent.y,
            'z':act.bounding_box.extent.z + 0.5
        }
        
        carla_obj_vehicle['debug_infos'].append(vehicle_debug_infos)
        #cam.listen(lambda img: process_img(img=img))
        print(act.get_location())
        
        print("Auto iD: ", act_snap.id)
        #print("WORLD TICK: ", w_id)
    else:
        print("Actor is not alive!")
        carla_obj['carla_object'].append(carla_obj_vehicle)
        #debug_to_json_file(carla_obj, "debug_infos")
    return obj_snap

def main():
    try:
        klient, welt, blueprint_lib = initialisiere_klient_instanz()
        
        wetter_einstellen(welt, 80.0, 1.0, 5.0)

        model_auto, auto_snapshot = fuege_neues_auto_hinzu(welt=welt,
                                        bp_lib=blueprint_lib,
                                        obj_location_int=0,
                                        obj_verfeinern='mercedes-benz.*')

        obj_lst.append(model_auto)

        sensor_lib = welt.get_blueprint_library().find('sensor.camera.rgb')
        sensor_bilder_einnahme_einstellen(sensor_lib)
        sensor, sensor_snapshot = fuege_neuer_sensor_hinzu(welt=welt,
                                        bp_lib=sensor_lib,
                                        verbundene_obj=model_auto)
        
        obj_lst.append(sensor)
        print("Auto-Snap:\n", auto_snapshot, "\nSensor-Snap:\n", sensor_snapshot)

        
        auto_verhalten_einstellen(model_auto, 1.0, 0.0)

        wege_typ = carla.LaneType.Driving | carla.LaneType.Sidewalk
        #weg_in_der_stadt_debuggen(welt=welt, auto_obj=model_auto, wege_projetieren=True, projektion_type=wege_typ)
        sensor.listen(lambda img: process_img(img=img))
        
        welt.on_tick(lambda auto_snapshot: on_debugging(auto_snapshot, welt, model_auto))
        time.sleep(6)
    
    finally:
        print("destroying actors...")
        for held in obj_lst:
            held.destroy()
        print("\nDone")

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        print("All is done!")