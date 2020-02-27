import os

from PIL import Image
import cv2
import json

class process_data_file:

    def __init__(self):
        print("Start ")


    #methode to draw the Box in a given image with top left point coordinate and height and width
    def draw_box(self,img,x,y,h,w):

        border=2

        new_image=cv2.rectangle(img, (x,y),(x+h,y+w),(0,0,255),border) #to draw a 2D box with given data

        return new_image

    #methode to draw the Box in a given image with top left point and bottom right point
    #this is the method actually used
    @staticmethod
    def draw_box_1(img,points,color):
        new_image=img

        print("#####################Drawing###############")
        print("numbers of rectangle to draw:",len(points))

        for point in points:
            p1=(point[0],point[1])
            p2=(point[2],point[3])
            print(p1,p2)
            border=1

            new_image=cv2.rectangle(new_image, p1,p2,color,border)

        return new_image
        
    
    #show the image in the given location
    @staticmethod
    def show_box(my_image):

        cv2.imshow("Image", my_image)

        cv2.waitKey(0)

        return
    
    
    #save the image in the given location with the given filename
    @staticmethod
    def save_image(filename,my_image):

        cv2.imwrite(filename,my_image)

        return

    #create the Json files to create the 2D Boxes of vehicle and walkers
    def save_json(vehicles_coordinates,walkers_coordinates,file_name):

        vehicles=[]
        walkers=[]
        json_object_dict={}

        vehicle_key="vehicles"
        walkers_key="walkers"
        min_x_key="min_x"
        max_x_key="max_x"
        min_y_key="min_y"
        max_y_key="max_y"
        number_of_walkers="number_of_walkers"
        number_of_vehicles = "number_of_vehicles"

        for point in vehicles_coordinates: #writing vehicles coordinate in the Json data
            new_vehicle={}
            min_x=point[0]
            min_y=point[1]
            max_x=point[2]
            max_y=point[3]

            new_vehicle[min_x_key]=min_x
            new_vehicle[max_x_key]=max_x
            new_vehicle[min_y_key]=min_y
            new_vehicle[max_y_key]=max_y

            vehicles.append(new_vehicle)

        for point in walkers_coordinates: # writting walkers coordinates in the json data
            new_walker = {}
            min_x = point[0]
            min_y = point[1]
            max_x = point[2]
            max_y = point[3]

            new_walker[min_x_key] = min_x
            new_walker[max_x_key] = max_x
            new_walker[min_y_key] = min_y
            new_walker[max_y_key] = max_y

            walkers.append(new_walker)

        json_object_dict[number_of_vehicles]=len(vehicles_coordinates)
        json_object_dict[vehicle_key]=vehicles
        json_object_dict[number_of_walkers]=len(walkers_coordinates)
        json_object_dict[walkers_key]=walkers

        with open(file_name, 'w') as json_file:
            json.dump(json_object_dict, json_file,indent=4,sort_keys=False) #saving the Json data in a Json file

    # read the config.ini file to get the path to the Original, Treated and Json files
    def read_List_Folder_Settings():
        settings_File_Name = "./config.ini" #location of the config.ini file (in this case in the same folder)
        prog_Location = os.path.dirname(__file__)
        settings_File_Location = os.path.join(prog_Location, settings_File_Name)
        folder_List = []
        try:

            with open(settings_File_Location, "r") as fp:
                line = fp.readline() #we read the first line in the file, this line containt the the path to the Original Folder
                cnt = 1
                while line:
                    print("Line {}: {}".format(cnt, line.rstrip('\n'))) 
                    folder_List.append(line.rstrip('\n')) #removing the caracter \n
                    line = fp.readline() #we read each line in the file, this file should containt only 3 lines in total
                    cnt += 1
        finally:
            fp.close()

        if (len(folder_List) == 0):
            print("No Folder found in settings File")
        else:
            print("Numbers of Folder in settings File:", len(folder_List))
            for x in folder_List:
                print(x)

        return folder_List
