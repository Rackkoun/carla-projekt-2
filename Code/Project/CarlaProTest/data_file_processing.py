import glob
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


	    #function call when we have clicked on "Start"

    #read The Json Files and return the Coordinates of Vehicles and Walkers


    def read_json():

        #saving the Location of our folders in variables
        path_name_original = process_data_file.read_List_Folder_Settings()[0] #original folder path
        path_name_treated = process_data_file.read_List_Folder_Settings()[1] #treated Folder Path
        path_name_json = process_data_file.read_List_Folder_Settings()[2] #Json Folder path

        new_path_name = path_name_json + "/*.json"
        files_list = glob.glob(new_path_name) #list all files with extension .json in the Json folder
        print("nomber of Json Files found:", len(files_list))

        #key to fetch data in the Json Files
        letters_to_delete = 9  #number of letter generated  for the filename
        vehicle_key = "vehicles"
        walkers_key = "walkers"
        min_x_key = "min_x"
        max_x_key = "max_x"
        min_y_key = "min_y"
        max_y_key = "max_y"


        original_absolute_path_name_list = []
        treated_absolute_path_name_list = []
        all_walkers_list = []
        all_vehicles_list = []

        for file in files_list:
            print("processing the Json File:",file)
            path, file_name = os.path.split(file) #we got here the parent path and the filename from the absolute path of the Json file
            print("Complet Filename:",file_name)
            json_file_name_only = file_name[0:len(file_name) - letters_to_delete] #we remoce the extension and the part"_Json" from the Json filename
            print("Json File Name only:",json_file_name_only)
            original_absolute_path_name = path_name_original + "/" + json_file_name_only + "Original.jpeg" #we reconstruct the Originale absolute path
            treated_absolute_path_name = path_name_treated + "/" + json_file_name_only + "Treated.jpeg" #we create the Treated absolute path

            print("trying to open original file:", original_absolute_path_name)
            print("trying to open json file:", file)

            if os.path.isfile(original_absolute_path_name) and os.path.isfile(file):
                print("original image file found and Json file found")
                
                #open the Json file and load all his content in a Json data variable
                with open(file) as f:
                    json_data = json.load(f)

                if (json_data != None):

                    original_absolute_path_name_list.append(original_absolute_path_name)
                    treated_absolute_path_name_list.append(treated_absolute_path_name)

                    print("Json File not empty and data Loaded")
                    vehicles = json_data[vehicle_key] #all the vehicles
                    walkers = json_data[walkers_key]  # all the walkers

                    all_vehicles = []
                    all_walkers = []
        
                    #fetch all the coordinates of vehicles
                    for vehicle in vehicles:
                        coordinate = (vehicle[min_x_key], vehicle[min_y_key], vehicle[max_x_key], vehicle[max_y_key])
                        all_vehicles.append(coordinate)
                    print("number of vehicles found:",len(all_vehicles))

                    #fetch all the coordinates of walkers
                    for walker in walkers:
                        coordinate = (walker[min_x_key], walker[min_y_key], walker[max_x_key], walker[max_y_key])
                        all_walkers.append(coordinate)

                    print("number of walkers found:", len(all_walkers))

                else:
                    print("No data found, Json file Empty or not opened properly")

            else:
                print("one of the file (Json or Original) not found")

            all_vehicles_list.append(all_vehicles)
            all_walkers_list.append(all_walkers)





        #we return original_absolute_path_name_list, treated_absolute_path_name_list, all_vehicles_all_walkers
        return original_absolute_path_name_list,treated_absolute_path_name_list,all_vehicles_list, all_walkers_list

                  

