import tkinter as tk
import time

from tkinter import ttk
from PIL import Image, ImageTk
from threading import Thread
from queue import Queue

from model.image_processing import CustomCarlaDataset

OBJ_ID = 'Object id'
OBJ_TYP = 'Object typ'


class MainApp(object):
    def __init__(self):
        print("Main class")
        self.main_window = tk.Tk()
        self.main_window.title("Project 2: WiSo19/20")
        self.main_window.resizable(0, 0)

        self.control_panel = ControlPanel(self.main_window)
        self.visualization_panel = VisualizationPanel(self.main_window)

        im, jfile, im_name = CustomCarlaDataset.on_getting_data(35)
        rearraged_img = CustomCarlaDataset.rearrang_img_for_gui(im)
        print(type(rearraged_img))
        self.visualization_panel.on_show_json_content(jfile)
        self.visualization_panel.on_show_img_original(rearraged_img)
        self.visualization_panel.on_show_img_copy(rearraged_img)


#########################################################
#              Layout of the application                #
#########################################################

class ControlPanel(object):

    def __init__(self, master):
        print("Control panel class")
        # top container of control panel
        self.frame = ttk.Frame(master, padding=(3, 3, 10, 10))
        self.frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        container = ttk.LabelFrame(master=self.frame, text='control panel')
        container.pack(padx=10, pady=5)

        # create tk variable
        self.entry_var = tk.IntVar()
        self.show_box_var = tk.IntVar()
        self.rdio_var = tk.IntVar()

        # container for file navigation
        nav_container = ttk.LabelFrame(container, text='File navigation', padding=(2, 2, 5, 5))
        nav_container.pack(side=tk.TOP, pady=10, padx=5)

        # adding elements int the navigation container
        label1 = ttk.Label(nav_container, text='Show')
        label1.grid(row=0, column=0, padx=8, pady=5, sticky='E')
        label11 = ttk.Label(nav_container, text='Image number:')
        label11.grid(row=0, column=1, padx=2, pady=5, sticky='W')

        entry = ttk.Entry(nav_container, width=5, textvariable=self.entry_var)
        entry.grid(row=0, column=2, padx=5, pady=5, sticky='E')

        self.prev_btn = ttk.Button(nav_container, text='prev')
        self.prev_btn.grid(row=1, column=0, padx=2, pady=5, sticky='W')

        self.dynamic_label = ttk.Label(nav_container, text='1/28')
        self.dynamic_label.grid(row=1, column=1, padx=2, pady=5)

        self.next_btn = ttk.Button(nav_container, text='next')
        self.next_btn.grid(row=1, column=2, padx=1, pady=5, sticky='E')

        # container for drawing 2D bbox and id for objects
        obj_detect_container = ttk.LabelFrame(container, text='Object detection', padding=(2, 2, 10, 10))
        obj_detect_container.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)

        self.show_box = tk.Checkbutton(obj_detect_container, text='Show 2D box', variable=self.show_box_var)
        self.show_box.pack(side=tk.TOP, anchor=tk.W, pady=5)

        id_container = ttk.LabelFrame(obj_detect_container, text='Show object label', padding=(2, 2, 10, 10))
        id_container.pack(side=tk.RIGHT, fill=tk.X, expand=tk.YES, padx=5, pady=10)

        self.id_rdio = tk.Radiobutton(id_container, text=OBJ_ID, variable=self.rdio_var, value=1)
        self.id_rdio.grid(row=0, column=0, padx=8, pady=5)
        self.typ_rdio = tk.Radiobutton(id_container, text=OBJ_TYP, variable=self.rdio_var, value=2)
        self.typ_rdio.grid(row=1, column=0, padx=8, pady=5)

        self.save_btn = ttk.Button(obj_detect_container, text='save')
        self.save_btn.pack(side=tk.LEFT, anchor='sw', padx=5, pady=10)


class VisualizationPanel(object):
    def __init__(self, master):
        print("Visualization panel class")
        # top container of control panel
        self.frame = ttk.Frame(master, padding=(3, 3, 10, 10))
        self.frame.pack(side=tk.RIGHT, pady=10, padx=5)

        container = ttk.LabelFrame(master=self.frame, text='visualization panel', padding=(2, 2, 10, 10))
        container.pack(padx=10, pady=5)

        self.origin_img_lbl = None
        self.copy_img_lbl = None

        self.json_file_container = ttk.LabelFrame(master=container, text='JSON-File content', padding=(2, 2, 10, 10))
        self.json_file_container.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

        self.img_orig_container = ttk.LabelFrame(master=container, text='Original', padding=(2, 2, 10, 10))
        self.img_orig_container.pack(side=tk.LEFT, pady=10)

        self.img_copy_container = ttk.LabelFrame(master=container, text='Copy', padding=(2, 2, 10, 10))
        self.img_copy_container.pack(side=tk.RIGHT, pady=10)



        # add a scrollbar to text widget
        scrollbar = tk.Scrollbar(self.json_file_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.json_content = tk.Text(self.json_file_container, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=15)
        self.json_content.pack(padx=8, pady=10)
        self.json_content.delete(1.0, tk.END)  # delete the content of text area

        scrollbar.config(command=self.json_content.yview)

    def on_show_img_original(self, img_arr):
        origin_img = Image.fromarray(img_arr)

        # resize the image to diplay on the GUI
        origin_img.thumbnail((420, 440), Image.ANTIALIAS)
        print(origin_img)
        img_lbl = ImageTk.PhotoImage(image=origin_img)
        self.origin_img_lbl = ttk.Label(self.img_orig_container, image=img_lbl)
        self.origin_img_lbl.pack(padx=8, pady=8)
        self.origin_img_lbl = img_lbl

    def on_show_img_copy(self, img_arr):
        origin_img = Image.fromarray(img_arr)

        # resize the image to diplay on the GUI
        origin_img.thumbnail((420, 440), Image.ANTIALIAS)
        print(origin_img)
        img_lbl = ImageTk.PhotoImage(image=origin_img)
        self.copy_img_lbl = ttk.Label(self.img_copy_container, image=img_lbl)
        self.copy_img_lbl.pack(padx=8, pady=8)
        self.copy_img_lbl = img_lbl

    def on_show_json_content(self, content):
        # delete the old content and put the new one
        print('current content')
        print(self.json_content.get(1.0, tk.END))
        self.json_content.delete(1.0, tk.END)
        # self.json_content.insert(tk.INSERT, str(content))
        print('######### start of json file ########## ')
        # print('{')
        self.json_content.insert(tk.INSERT, '{\n')
        for k, v in content.items():
            if isinstance(v, dict):
                # print('\t', k, ':{')
                self.json_content.insert(tk.INSERT, '\t' + '\"' + str(k) + '\"' + ':' + '{\n')
                for nk, nv in v.items():
                    if isinstance(nv, dict):
                        # print('\t\t', nk, ':', '{')
                        self.json_content.insert(tk.INSERT, '\t\t' + '\"' + str(nk) + '\":{\n')
                        for nnk, nnv in nv.items():
                            # print('\t\t\t', nnk, ':', nnv, ',')
                            self.json_content.insert(tk.INSERT, '\t\t\t' + '\"' + str(nnk) + '\":' + str(nnv) + ',\n')
                        # print('\t\t}')
                        self.json_content.insert(tk.INSERT, '\t\t},\n')
                    elif isinstance(nv, list):
                        pass
                    else:
                        # print('\t\t', nk, ':', nv, ',')
                        self.json_content.insert(tk.INSERT, '\t\t\"' + str(nk) + '\":' + str(nv) + ',\n')
                # print('\t},')
                self.json_content.insert(tk.INSERT, '\t},\n')
            elif isinstance(v, list):
                # print('\t', k, ':[')
                self.json_content.insert(tk.INSERT, '\t\"' + str(k) + '\":[\n')
                for elem in v:
                    # print('\t\t{')
                    self.json_content.insert(tk.INSERT, '\t\t{\n')
                    if isinstance(elem, dict):
                        for nk_elem, nv_elem in elem.items():
                            if isinstance(nv_elem, dict):
                                # print('\t\t\t\t', nk_elem, ': {')
                                self.json_content.insert(tk.INSERT, '\t\t\t\t\"' + str(nk_elem) + '\":{\n')
                                for nnk_elem, nnv_elem in nv_elem.items():
                                    # print('\t\t\t\t\t', nnk_elem, ':', nnv_elem, ',')
                                    self.json_content.insert(tk.INSERT, '\t\t\t\t\t\"' + str(nnk_elem) + '\":' + str(nnv_elem) + ',\n')
                                # print('\t\t\t\t},')
                                self.json_content.insert(tk.INSERT, '\t\t\t\t},\n')
                            else:
                                # print('\t\t\t\t', nk_elem, ':', nv_elem, ',')
                                self.json_content.insert(tk.INSERT, '\t\t\t\t\"' + str(nk_elem) + '\":' + str(nv_elem) + ',\n')
                    # print('\t\t},')
                    self.json_content.insert(tk.INSERT, '\t\t},\n')
                # print('\t]')
                self.json_content.insert(tk.INSERT, '\t]\n')
            else:
                # print('\t', k, ': ', v, ',')
                self.json_content.insert(tk.INSERT, '\t\"' + str(k) + '\":' + str(v) + ',\n')
        # print('}')
        self.json_content.insert(tk.INSERT, '\n}')
        print('######## end of json ########')


if __name__ == '__main__':
    app = MainApp()
    app.main_window.mainloop()
