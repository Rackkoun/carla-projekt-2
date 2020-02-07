import tkinter as tk

from tkinter import ttk
from PIL import Image, ImageTk

from model.image_processing import CustomCarlaDataset, ObjectDetectionWithOpenCV

# from image_processing import CustomCarlaDataset

OBJ_ID = 'Object id'
OBJ_TYP = 'Object typ'


class MainApp(object):

    def __init__(self):
        print("Main class")
        self.main_window = tk.Tk()
        self.main_window.title("Project 2: WiSo19/20")
        # self.main_window.geometry('1267x914')

        im_lst, json_lst = CustomCarlaDataset.load()
        self.main_panel = MainPanel(self.main_window, len(im_lst))
        print(len(im_lst), len(json_lst))
        print(type(im_lst))


#########################################################
#              Layout of the application                #
#########################################################

class MainPanel(object):

    def __init__(self, master, max_length):
        # main frame
        root_panel = ttk.Frame(master)
        root_panel.pack()

        # create panels for control and visualization
        # top container of control panel
        self.frame_control = ttk.Frame(root_panel, padding=(4, 4, 4, 4))
        self.frame_control.pack(side=tk.LEFT, fill=tk.Y, pady=10)

        # top container of Visualization panel
        self.frame_visualization = ttk.Frame(root_panel, padding=(3, 3, 3, 3))
        self.frame_visualization.pack(side=tk.RIGHT, pady=4, padx=5)

        container_control = ttk.LabelFrame(master=self.frame_control, text='control panel', padding=(3, 3, 3, 3))
        container_control.pack(padx=4, pady=5)

        # create tk variable
        self.entry_var = tk.IntVar()
        self.entry_var.set(1)
        self.show_box_var = tk.IntVar()
        self.rdio_var = tk.IntVar()
        self.lbl_var = tk.StringVar()

        self.count = tk.IntVar()
        print("self.count:", self.count.get())
        self.max_count = tk.IntVar()
        self.max_count.set(max_length - 1)
        print("self.max_count:", self.max_count.get())
        self.lbl_var.set('{}/{}'.format(self.count.get() + 1, self.max_count.get() + 1))

        # container for file navigation
        nav_container = ttk.LabelFrame(container_control, text='File navigation', padding=(3, 2, 2, 3))
        nav_container.pack(side=tk.TOP, pady=4, padx=5, fill=tk.X)

        # adding elements int the navigation container
        label1 = ttk.Label(nav_container, text='go to')
        label1.grid(row=0, column=0, padx=2, pady=5, sticky='E')
        label11 = ttk.Label(nav_container, text='image number:')
        label11.grid(row=0, column=1, padx=2, pady=5, sticky='W')

        self.entry = ttk.Entry(nav_container, width=5, textvariable=self.entry_var)
        self.entry.grid(row=0, column=2, padx=5, pady=5, sticky='E')
        self.entry.bind('<Return>', self.on_enter_pressed)
        self.prev_btn = ttk.Button(nav_container, text='prev', command=self.on_prev_clicked)
        self.prev_btn.grid(row=1, column=0, padx=2, pady=5, sticky='W')

        self.dynamic_label = ttk.Label(nav_container, textvariable=self.lbl_var)
        self.dynamic_label.grid(row=1, column=1, pady=5)

        self.next_btn = ttk.Button(nav_container, text='next', command=self.on_next_clicked)
        self.next_btn.grid(row=1, column=2, padx=1, pady=5, sticky='E')

        action_container = ttk.LabelFrame(container_control, text='Save File(s)', padding=(3, 3, 3, 3))
        action_container.pack(side=tk.BOTTOM, fill=tk.X, expand=tk.YES, padx=5, pady=10)

        # self.typ_rdio = tk.Radiobutton(action_container, text=OBJ_TYP, variable=self.rdio_var, value=2)
        # self.typ_rdio.grid(row=1, column=0, padx=8, pady=5)

        self.save_current_btn = ttk.Button(action_container, text='save current img', command=self.on_save)
        self.save_current_btn.pack(side=tk.LEFT, padx=5, pady=10)

        self.save_all_btn = ttk.Button(action_container, text='save all img', command=self.on_save_all)
        self.save_all_btn.pack(side=tk.RIGHT, padx=5, pady=10)

        # container for drawing 2D bbox and id for objects
        self.detected_obj_container = ttk.LabelFrame(container_control, text='Detected object info', padding=(3, 3, 3, 3))
        self.detected_obj_container.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)

        # self.show_box = tk.Checkbutton(obj_detect_container, text='Show 2D box', variable=self.show_box_var)
        # self.show_box.pack(side=tk.TOP, anchor=tk.W, pady=5)
        self.info_entry = tk.Text(self.detected_obj_container, wrap=tk.WORD, height=8, width=50)
        self.info_entry.pack(padx=8, pady=5)
        # Visualization
        self.container_visualization = ttk.LabelFrame(master=self.frame_visualization, text='visualization panel',
                                                      padding=(3, 3, 3, 3))
        self.container_visualization.pack()

        # load all files and set the max size

        self.origin_img_lbl = None
        self.copy_img_lbl = None

        # VisualizationPanel.MAX_COUNT = max_count
        print('len of pic: ', self.max_count.get())
        # ControlPanel.MAX_COUNT = VisualizationPanel.MAX_COUNT

        self.json_file_container = ttk.LabelFrame(master=self.container_visualization, text='JSON-File content',
                                                  padding=(2, 2, 2, 2))
        self.json_file_container.pack(side=tk.BOTTOM, pady=10, fill=tk.X)

        self.img_orig_container = ttk.LabelFrame(master=self.container_visualization, text='Original',
                                                 padding=(2, 2, 2, 2))
        self.img_orig_container.pack(side=tk.LEFT)

        self.img_copy_container = ttk.LabelFrame(master=self.container_visualization, text='Copy',
                                                 padding=(2, 2, 2, 2))
        self.img_copy_container.pack(side=tk.RIGHT)

        # add a scrollbar to text widget
        scrollbar = tk.Scrollbar(self.json_file_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.json_content = tk.Text(self.json_file_container, wrap=tk.WORD, yscrollcommand=scrollbar.set, height=15)
        self.json_content.pack(padx=8, pady=10)
        self.json_content.delete(1.0, tk.END)  # delete the content of text area

        scrollbar.config(command=self.json_content.yview)

        self.origin_img_lbl = ttk.Label(self.img_orig_container, image=None)
        self.origin_img_lbl.pack(padx=8, pady=8)

        self.copy_img_lbl = ttk.Label(self.img_copy_container, image=None)
        self.copy_img_lbl.pack(padx=8, pady=8)

        # display picture
        self.on_show_img_original(self.count.get())
        self.on_show_img_copy(self.count.get())
        self.on_show_json_content(self.count.get())
        # self.on_show_detected_obj()

        if self.count.get() - 1 <= 0:
            print("got the first Image")
            self.prev_btn.config(state="disabled")

        if self.count.get() + 1 >= self.max_count.get():
            print("got the last Image")
            self.next_btn.config(state="disabled")

    def on_next_clicked(self):
        if self.count.get() < self.max_count.get():
            if self.count.get() + 1 >= self.max_count.get():
                print("got the last Image")
                self.next_btn.config(state="disabled")
            # MainPanel2.COUNT += 1
            self.count.set(self.count.get() + 1)

            if self.count.get() > 0:
                self.prev_btn.config(state="normal")

            # pass the result to a function
            self.on_show_img_original(self.count.get())
            self.on_show_img_copy(self.count.get())
            self.on_show_json_content(self.count.get())
            self._on_update_text()
        else:
            self.count.set(self.max_count.get())
            # self.count_var.set(count)
            self.on_show_img_original(self.count.get())
            self.on_show_img_copy(self.count.get())
            self.on_show_json_content(self.count.get())
            self._on_update_text()

    def on_prev_clicked(self):
        if self.count.get() > 0:

            if self.count.get() - 1 <= 0:
                print("got the first Image")
                self.prev_btn.config(state="disabled")

            self.count.set(self.count.get() - 1)

            if self.count.get() < self.max_count.get():
                self.next_btn.config(state="normal")

            self.on_show_img_original(self.count.get())
            self.on_show_img_copy(self.count.get())
            self.on_show_json_content(self.count.get())
            self._on_update_text()
        else:
            self.count.set(0)
            self.on_show_img_original(self.count.get())
            self.on_show_img_copy(self.count.get())
            self.on_show_json_content(self.count.get())
            self._on_update_text()

    def _on_update_text(self):
        self.lbl_var.set('{}/{}'.format(self.count.get() + 1, self.max_count.get() + 1))
        print('label updated: {}/{}'.format(self.count.get() + 1, self.max_count.get() + 1))

    def on_enter_pressed(self, event):
        """
        Method to get value in the entry field and display the data at the given position

        :param event:
        :return:
        """
        self.entry.setvar(self.entry.get())
        print('VAR: ', int(self.entry.get()))
        self.count.set(int(self.entry.get()))
        self.on_show_img_original(self.count.get())
        self.on_show_img_copy(self.count.get())
        self.on_show_json_content(self.count.get())
        self._on_update_text()

    def on_save(self):
        print('SAVE PRESSED')
        count = self.count.get()
        img_arr, img_name = CustomCarlaDataset.on_load_img(count)
        img_info = CustomCarlaDataset.on_load_file(count)

        box_img_arr, lbl_id, lbl_typ, box_coord = ObjectDetectionWithOpenCV.on_draw(img_arr, img_info)
        ObjectDetectionWithOpenCV.on_saving_copy(box_img_arr, img_name)

    def on_save_all(self):
        print('Saving...')
        count = 0
        max_count = self.max_count.get()
        while count < max_count:
            img_arr, img_name = CustomCarlaDataset.on_load_img(count)
            img_info = CustomCarlaDataset.on_load_file(count)

            box_img_arr, lbl_id, lbl_typ, box_coord = ObjectDetectionWithOpenCV.on_draw(img_arr, img_info)
            ObjectDetectionWithOpenCV.on_saving_copy(box_img_arr, img_name)

            count += 1

        print('Finish')

    def on_show_detected_obj(self, id_lst, class_lst, coor_lst):
        self.info_entry.delete(1.0, tk.END)
        self.info_entry.insert(tk.INSERT, 'Id \tClass \tP0 \tP1 \tP2 \tP3\n')
        for _id, _class, _coord in zip(id_lst, class_lst, coor_lst):
            _p0 = _coord[0]
            _p1 = _coord[1]
            _p2 = _coord[2]
            _p3 = _coord[3]
            print('ID: ', _id, ' class: ', _class, _p0, _p1, _p2, _p3)
            self.info_entry.insert(tk.INSERT, str(_id)+' \t'+str(_class)+'\t'+str(_p0)+'\t'+str(_p1)+'\t'+str(_p2)+'\t'+str(_p3)+'\n')
        #
        # print('get TEXT')
        # text = self.info_entry.get(1.0, tk.END)
        # print(text)

    def on_show_img_original(self, count):
        print('on show original')
        array_img, img_name = CustomCarlaDataset.on_load_img(count)
        re_arrange = CustomCarlaDataset.rearrang_img_for_gui(array_img)
        origin_img = Image.fromarray(re_arrange)
        # resize the image to diplay on the GUI
        origin_img.thumbnail((420, 440), Image.ANTIALIAS)
        img_lbl = ImageTk.PhotoImage(image=origin_img)
        print("LABL: ", img_lbl.height())
        print('ENTRY: ', self.entry_var.get())
        self.origin_img_lbl.configure(image=img_lbl, anchor=tk.NW)
        # self.origin_img_lbl = ttk.Label(self.img_orig_container, image=img_lbl)
        self.origin_img_lbl.image = img_lbl
        self.origin_img_lbl.pack(padx=8, pady=8)

    def on_show_img_copy(self, count):
        img_arr, img_name = CustomCarlaDataset.on_load_img(count)
        img_info = CustomCarlaDataset.on_load_file(count)

        box_img_arr, lbl_id, lbl_typ, box_coord = ObjectDetectionWithOpenCV.on_draw(img_arr, img_info)
        box_re_arranged = CustomCarlaDataset.rearrang_img_for_gui(box_img_arr)
        re_arrange = CustomCarlaDataset.rearrang_img_for_gui(img_arr)
        origin_img = Image.fromarray(re_arrange)
        box_copy_img = Image.fromarray(box_re_arranged)

        self.on_show_detected_obj(lbl_id, lbl_typ, box_coord)

        # resize the image to diplay on the GUI
        origin_img.thumbnail((420, 440), Image.ANTIALIAS)
        box_copy_img.thumbnail((420, 440), Image.ANTIALIAS)
        img_lbl = ImageTk.PhotoImage(image=box_copy_img)
        self.copy_img_lbl.configure(image=img_lbl, anchor=tk.NW)
        # self.copy_img_lbl = ttk.Label(self.img_copy_container, image=img_lbl)
        self.copy_img_lbl.image = img_lbl
        self.copy_img_lbl.pack(padx=8, pady=8)

    def on_show_json_content(self, count):
        print('JSON ', count)
        content = CustomCarlaDataset.on_load_file(count)
        # delete the old content and put the new one
        self.json_content.delete(1.0, tk.END)
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
                                self.json_content.insert(tk.INSERT, '\t\t\t\"' + str(nk_elem) + '\":{\n')
                                for nnk_elem, nnv_elem in nv_elem.items():
                                    # print('\t\t\t\t\t', nnk_elem, ':', nnv_elem, ',')
                                    self.json_content.insert(tk.INSERT, '\t\t\t\t\"' + str(nnk_elem) + '\":' + str(
                                        nnv_elem) + ',\n')
                                # print('\t\t\t\t},')
                                self.json_content.insert(tk.INSERT, '\t\t\t},\n')
                            else:
                                # print('\t\t\t\t', nk_elem, ':', nv_elem, ',')
                                self.json_content.insert(tk.INSERT,
                                                         '\t\t\t\"' + str(nk_elem) + '\":' + str(nv_elem) + ',\n')
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
