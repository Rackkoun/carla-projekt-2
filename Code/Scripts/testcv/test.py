import cv2 as cv
import json

def on_load_file(file_content):
    # file_content = file_content.read_text()
    with open(file_content, encoding='utf-8') as data:
        json_file = json.load(data)
        return json_file

def get_obj(dico):
    obj = []
    for o in dico['object']:
        obj.append(o)
    return obj

def open_img(im):
    im_array = cv.imread(im)
    return im_array

def show_img(ima, im_name, info):
    # draw rectangle
    for obj in info:
        box_img = cv.rectangle(
            ima,
            (obj['P0'], obj['P1']),
            (obj['P2'], obj['P3']),
            (0, 255, 0),
            2
        )
        cv.putText(box_img,
        str(obj['Class']),
        (obj['P0'], obj['P1'] - 10),
        cv.FONT_HERSHEY_PLAIN,
        0.8,
        (255, 255, 255))

    print(type(box_img))
    cv.imshow(im_name, box_img)
    cv.waitKey(0)
    cv.destroyAllWindows()

if __name__=='__main__':

    content = on_load_file('copy-1003.json')
    content_array = get_obj(content)

    im_arr = open_img('1003.png')
    print(type(im_arr))
    print(content_array[2])
    show_img(im_arr, 'copy-img', content_array)
    