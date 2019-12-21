import cv2

class Draw_Box_On_Image:

    def __init__(self):
        print("Start")


    def draw_box(self,img,x,y,h,w):

        border=2

        new_image=cv2.rectangle(img, (x,y),(x+h,y+w),(0,0,255),border)

        return new_image

    def show_box(self,my_image):

        cv2.imshow("Image", my_image)

        cv2.waitKey(0)

        return

    def save_image(self,filename,my_image):

        cv2.imwrite(filename,my_image)

        return


    def main(self):

        # exemple with an image with 3 object to label

        image_name = "carla_test_image.jpg"

        image_array = cv2.imread(image_name)

        x = 1048    # xmin

        y = 457     # ymin

        h = 108     # height

        w = 71      # width

        my_new_image_array = self.draw_box(image_array,x,y,h,w)

        print("first Box generated")

        x = 1442

        y = 346

        h = 21

        w = 49

        my_new_image_array = self.draw_box(my_new_image_array,x,y,h,w)

        x = 88

        y = 462

        h = 210

        w = 100

        my_new_image_array = self.draw_box(my_new_image_array, x, y, h, w)

        self.show_box(my_new_image_array)   # press c to quit the image

        self.save_image("labeled_image_test.jpg",my_new_image_array)  # saving the image on the folder

if __name__ == "__main__":

    test_draw=Draw_Box_On_Image()

    test_draw.main()
    
    #                   witdh
    #   (x,y)-----------------------
    #      |                        |
    #      |                        |
    #      |                        | height
    #      |                        |
    #      |                        |
    #      |________________________|(x+height, y+width)
