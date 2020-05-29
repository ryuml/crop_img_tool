# coding: utf-8

'''
crop_img_tool

Copyright (c) 2020 ryuml

This software is released under the MIT License.
http://opensource.org/licenses/mit-license.php
'''


#from Tkinter import *   # for Python2
from tkinter import *   # for Python3
from PIL import Image, ImageTk, ImageFile
import os
import sys
import shutil
import io


# for avoiding errors of resizing image error
#ImageFile.LOAD_TRUNCATED_IMAGES = True


# >>> environment params --------------------
# canvas size
CANVAS_SIZE = (1120, 480)
# default size
DEF_WIDTH = 640
DEF_HEIGHT = 480
# canvas limit
CANVAS_W_MAX = 1120
CANVAS_H_MAX = 600

# a directory of original images
IM_DIR = './org_images'

# a directory for resized images
RE_IM_DIR = 'resized_images'
if not os.path.isdir(RE_IM_DIR):
    os.mkdir(RE_IM_DIR)
# a directory of cropped images
CR_IM_DIR = './cropped_images'
if not os.path.isdir(CR_IM_DIR):
    os.mkdir(CR_IM_DIR)
# a directory of skip images by copying
SK_IM_DIR = './skip_images'
if not os.path.isdir(SK_IM_DIR):
    os.mkdir(SK_IM_DIR)
# saving base name
SAVE_BASE_NAME = 'cropped_images'
# saving base name max length
SAVE_NAME_MAX = 30
# saving filename extension
SAVE_EXT = 'jpg'
# <<< environment params --------------------



# >>> class MainWindow ----------------------------------------------------------------------
class MainWindow():
    # >>> init function ----------------
    def __init__(self, main):
        # make canvas for displaying images
        self.canvas = Canvas(main, width=CANVAS_W_MAX, height=CANVAS_H_MAX)
        # debug
        print('\n>>> Canvas width: {}, height: {}'.format(
            CANVAS_W_MAX, CANVAS_H_MAX))
        self.canvas.grid(row=0, column=0, columnspan=3, rowspan=3)

        # load images and loading image parameters
        self.my_images = []
        self.my_img_paths = []
        tmp_cnt = 0
        skip_cnt = 0
        for im_name in sorted(os.listdir(IM_DIR)):
            im_path = os.path.join(IM_DIR, im_name)
            new_im_path = os.path.join(RE_IM_DIR,
                            os.extsep.join([os.path.splitext(im_name)[0], SAVE_EXT]) )
            try:
                # default
                im = Image.open(im_path)
                '''
                # corresponding to loading progressive JPEGs
                #   -> reference: "https://github.com/python-pillow/Pillow/issues/2717"
                with open(im_path, 'rb') as f:
                    im = Image.open(io.BytesIO(f.read() + b'\xff\xd9'))
                '''

            except Exception as e:
                print('\n  >> [Loading image Error] Cannot load: {}'.format(im_name))
                print('  -> Error type:\n  > ' + str(e))
                print('  -> Skip image...')

            # for debugging
            '''
            print(im.size)
            print('canvas size: ' + str(CANVAS_SIZE))
            print('r1: ' + str(CANVAS_SIZE[0] / im.size[0]))
            print('r2: ' + str(CANVAS_SIZE[1] / im.size[1]))
            '''

            # calculate a ratio of image edges
            r = 1.0 * CANVAS_SIZE[1] / im.size[1]   # adjust canvas height (default)
            if int(r * im.size[0]) < DEF_WIDTH:
                # width is smaller than default width
                print('\n > adjust default width.')
                r = 1.0 * CANVAS_SIZE[0] / im.size[0]   # adjust default width
                if int(r * im.size[1]) > CANVAS_H_MAX:
                    # height is bigger than canvas height max
                    print('\n > height: {} > canvas height max: {}.'.format(
                        int(r * im.size[1]), CANVAS_H_MAX))
                    print(' > [skip] image: {}, and copy skip dir: {}.'.format(
                        im_path, SK_IM_DIR))
                    # copy image to skip dir
                    shutil.copy2(im_path, SK_IM_DIR)
                    # update count
                    skip_cnt += 1
                    continue
            elif int(r * im.size[0]) > CANVAS_W_MAX:
                # width is bigger than canvas width max
                print('\n > width: {} > canvas width max: {}.'.format(
                    int(r * im.size[0]), CANVAS_W_MAX))
                print(' > [skip] image: {}, and copy skip dir: {}.'.format(
                    im_path, SK_IM_DIR))
                # copy image to skip dir
                shutil.copy2(im_path, SK_IM_DIR)
                # update count
                skip_cnt += 1
                continue

            #print('r: {}'.format(r))   # for debugging

            # change canvas size
            #self.canvas.configure(height=CANVAS_SIZE[1])   # aouto resizeing??
            new_size = int(r * im.size[0]), int(r * im.size[1])

            # print(new_size)   # for debugging

            # resizing
            try:
                new_im = im.resize(new_size, Image.ANTIALIAS)
                # save resized new image
                new_im.save(new_im_path)
                # loading images
                self.my_images.append(ImageTk.PhotoImage(new_im))
            except Exception as e:
                print('\n  >> [Resize image Error] Cannot Resize: {}'.format(im_name))
                print('  -> Resize: from-{} >-> to-{}'.format(im.size, new_size))
                print('  -> Error type:\n  > ' + str(e))
                if 'broken data' in str(e):
                    print(' -> May be, org_images folder contains a progressive image.')
                    print(' -> This application does not support progressive image format.')
                    print(' -> Quit application, because org_images folder contains broken data.')
                    quit()

                print('  -> Skip image...')

            # for debugging
            '''
            print('resized image size:')
            print(new_im.size)
            '''

            # adding file path list
            self.my_img_paths.append(new_im_path)

            # monitoring progress
            sys.stderr.write('\r -> resizing count: {}, name: {}{}'.format(tmp_cnt,
                                                                           im_name, ' ' * 30))
            sys.stderr.flush()
            tmp_cnt += 1
        sys.stderr.write('\n')
        sys.stderr.flush()

        # skip image count
        print('\n > [Skip] image count: {}'.format(skip_cnt))

        # number of image files
        self.im_num = len(self.my_img_paths)
        self.my_image_number = 0

        # setting number for saving images
        self.save_file_num = 0
        # saving image file base name
        self.save_base_name = SAVE_BASE_NAME

        # setting the first image
        self.image_on_canvas = self.canvas.create_image(
            0, 0, anchor=NW, image=self.my_images[self.my_image_number])

        # --- make buttons
        # button for displaying next image
        self.button_next = Button(
            main, text="Next", command=self.onNextButton, width=6, height=2)
        self.button_next.grid(row=3, column=3, columnspan=1, rowspan=1)
        # button for displaying preview image
        self.button_back = Button(
            main, text="Back", command=self.onBackButton, width=6)
        self.button_back.grid(row=4, column=3, columnspan=1)
        # button for saving selected region
        self.button_save = Button(
            main, text="Save", command=self.onSaveButton, width=13, height=2)
        self.button_save.grid(row=3, column=4, columnspan=1, rowspan=1)
        # button for returning number for saving
        self.button_saveb = Button(
            main, text="Save Back", command=self.onSavebButton, width=13)
        self.button_saveb.grid(row=4, column=4, columnspan=1)

        # --- make Entries for displaying message
        # a Entry for displaying current image number
        self.message_num = Entry(width=100)
        self.message_num.insert(
            END, ("This image is " + self.filenameMaker(self.my_image_number)))
        self.message_num.grid(row=5, column=0, columnspan=1)
        # a Entry for displaying next saving number
        self.message = Entry(width=100)
        self.message.insert(END, ' '.join(["Next save-name is", self.get_save_im_path()]))
        self.message.grid(row=6, column=0, columnspan=1)
        # a Entry for displaying current image size
        self.message_size = Entry(width=23)
        self.message_size.insert(
            END, (''.join(['size: ( ', str(self.my_images[self.my_image_number].width()),
                           ', ', str(self.my_images[self.my_image_number].height()), ' )'])) )
        self.message_size.grid(row=5, column=3, columnspan=2, rowspan=1)
        # a Entry for displaying current image number
        self.message_im_num = Entry(width=20)
        self.message_im_num.insert(
            END, (''.join(['number: ', str(self.my_image_number + 1), ' / ',
                           str(len(self.my_images))]) ) )
        self.message_im_num.grid(row=6, column=3, columnspan=2, rowspan=1)

        # --- make Entries and Buttons for displaying and setting save name params
        # Entries
        self.saving_num_entry = Entry(width=(len(str(self.im_num)) + 2) )
        self.saving_num_entry.insert(END, str(self.save_file_num + 1))
        self.saving_num_entry.grid(row=5, column=1, columnspan=1)
        self.s_base_name_entry = Entry(width=SAVE_NAME_MAX)
        self.s_base_name_entry.insert(END, self.save_base_name)
        self.s_base_name_entry.grid(row=6, column=1, columnspan=1)
        # Buttons
        self.s_num_set_button = Button(
            main, text="Set Num", command=self.onSavingNumSetButton, width=8, height=1)
        self.s_num_set_button.grid(row=5, column=2, columnspan=1, rowspan=1)
        self.s_b_nam_set_button = Button(
            main, text="Set Name", command=self.onSvingBNamSetButton, width=8, height=1)
        self.s_b_nam_set_button.grid(row=6, column=2, columnspan=1, rowspan=1)

        # for slider parameter
        self.left = 0
        self.right = 0
        self.top = 0
        self.bottom = 0

        # draw lines for cropping a image to the canvas
        self.canvas.create_line(self.left, 0, self.left,
                                200, tag="left_line", fill='green')
        self.canvas.create_line(self.right, 0, self.right,
                                200, tag="right_line", fill='red')
        self.canvas.create_line(
            0, self.top, 200, self.top, tag="top_line", fill='green')
        self.canvas.create_line(0, self.bottom, 200,
                                self.bottom, tag="bottom_line", fill='red')

        # --- make sliders for cropping a image
        self.left = Scale(main, label='left', orient='h',
                          from_=0, to=self.my_images[self.my_image_number].width(),
                          length=(CANVAS_W_MAX - 250),
                          command=self.onSliderLeft)
        self.left.grid(row=3, column=0, columnspan=1, rowspan=1)
        self.right = Scale(main, label='right', orient='h',
                           from_=0, to=self.my_images[self.my_image_number].width(),
                           length=(CANVAS_W_MAX - 250),
                           command=self.onSliderRight)
        self.right.grid(row=4, column=0, columnspan=1, rowspan=1)
        self.top = Scale(main, label='top', orient='v',
                         from_=0, to=self.my_images[self.my_image_number].height(),
                         length=(CANVAS_H_MAX - 100), command=self.onSliderTop)
        self.top.grid(row=0, column=3, rowspan=1)
        self.bottom = Scale(main, label='bottom', orient='v',
                            from_=0, to=self.my_images[self.my_image_number].height(),
                            length=(CANVAS_H_MAX - 100), command=self.onSliderBottom)
        self.bottom.grid(row=0, column=4, rowspan=1)

        # moving with adjusting a image displaying a line for cropping a image
        self.left.set(0)
        self.right.set(self.my_images[self.my_image_number].width())
        self.top.set(0)
        self.bottom.set(self.my_images[self.my_image_number].height())

        # --- make a Entries and Buttons for cropping a image
        # button for left param [L, plus(+)]
        self.left_button = Button(
            main, text='[+]', command=self.onLRTB_Button('L+'), width=5, height=1)
        self.left_button.grid(row=3, column=1, columnspan=1, rowspan=1)
        # button for left param [L, minus(-)]
        self.left_button = Button(
            main, text='[-]', command=self.onLRTB_Button('L-'), width=5, height=1)
        self.left_button.grid(row=3, column=2, columnspan=1, rowspan=1)
        # button for right param [R, plus(+)]
        self.right_button = Button(
            main, text='[+]', command=self.onLRTB_Button('R+'), width=5, height=1)
        self.right_button.grid(row=4, column=1, columnspan=1, rowspan=1)
        # button for right param [R, minux(-)]
        self.right_button = Button(
            main, text='[-]', command=self.onLRTB_Button('R-'), width=5, height=1)
        self.right_button.grid(row=4, column=2, columnspan=1, rowspan=1)
        # button for right param [T, plus(+)]
        self.right_button = Button(
            main, text='[+]', command=self.onLRTB_Button('T+'), width=5, height=1)
        self.right_button.grid(row=1, column=3, columnspan=1, rowspan=1)
        # button for right param [T, minux(-)]
        self.right_button = Button(
            main, text='[-]', command=self.onLRTB_Button('T-'), width=5, height=1)
        self.right_button.grid(row=2, column=3, columnspan=1, rowspan=1)
        # button for right param [B, plus(+)]
        self.right_button = Button(
            main, text='[+]', command=self.onLRTB_Button('B+'), width=5, height=1)
        self.right_button.grid(row=1, column=4, columnspan=1, rowspan=1)
        # button for right param [B, minux(-)]
        self.right_button = Button(
            main, text='[-]', command=self.onLRTB_Button('B-'), width=5, height=1)
        self.right_button.grid(row=2, column=4, columnspan=1, rowspan=1)
    # <<< init function ----------------


    # >>> button functions ---------------
    def onBackButton(self):
        # return to ending image
        if self.my_image_number == 0:
            self.my_image_number = len(self.my_images) - 1
        else:
            # return one time
            self.my_image_number -= 1

        # update displaying image
        self.canvas.itemconfig(self.image_on_canvas,
                               image=self.my_images[self.my_image_number])

        # update position of a line for cropping a image with adjusting displayed image
        self.left.set(0)
        self.right.set(self.my_images[self.my_image_number].width())
        self.top.set(0)
        self.bottom.set(self.my_images[self.my_image_number].height())

        # --- update contents of Entries
        # image path
        self.message_num.delete(0, END)
        self.message_num.insert(
            END, ("This image is " + self.filenameMaker(self.my_image_number)))
        # image size
        self.message_size.delete(0, END)
        self.message_size.insert(
            END, (''.join(['size: ( ', str(self.my_images[self.my_image_number].width()),
                           ', ', str(self.my_images[self.my_image_number].height()), ' )'])))
        # image number
        self.message_im_num.delete(0, END)
        self.message_im_num.insert(
            END, (''.join(['number: ', str(self.my_image_number + 1), ' / ',
                           str(len(self.my_images))])))

        # update sliders
        self.update_sliders()
        # update saving param entries
        self.update_saving_param_entries()
        # update lines
        self.update_lines()

    def onNextButton(self):
        # proceed one time
        self.my_image_number += 1

        # return to first image
        if self.my_image_number == len(self.my_images):
            self.my_image_number = 0

        # update displaying image
        self.canvas.itemconfig(self.image_on_canvas,
                               image=self.my_images[self.my_image_number])

        # update position of a line for cropping a image with adjusting displayed image
        self.left.set(0)
        self.right.set(self.my_images[self.my_image_number].width())
        self.top.set(0)
        self.bottom.set(self.my_images[self.my_image_number].height())

        # --- update contents of Entries
        # image path
        self.message_num.delete(0, END)
        self.message_num.insert(
            END, ("This image is " + self.filenameMaker(self.my_image_number)))
        # image size
        self.message_size.delete(0, END)
        self.message_size.insert(
            END, (''.join(['size: ( ', str(self.my_images[self.my_image_number].width()),
                           ', ', str(self.my_images[self.my_image_number].height()), ' )'])))
        # image number
        self.message_im_num.delete(0, END)
        self.message_im_num.insert(
            END, (''.join(['number: ', str(self.my_image_number + 1), ' / ',
                           str(len(self.my_images))])))

        # update sliders
        self.update_sliders()
        # update saving param entries
        self.update_saving_param_entries()
        # update lines
        self.update_lines()

    def onSaveButton(self):
        # loading displayed image
        temp_image = Image.open(self.filenameMaker(self.my_image_number))
        # cropping selected position
        cropped_image = temp_image.crop(
            (self.left.get(), self.top.get(), self.right.get(), self.bottom.get()))
        # saving a image
        cropped_image.save(self.get_save_im_path())

        # update counter for saving file
        self.save_file_num += 1

        # update contents of Entry
        self.message.delete(0, END)
        self.message.insert(END, ' '.join(["Next save-name is:", self.get_save_im_path()]))
        # update saving param entries
        self.update_saving_param_entries()

    def onSavebButton(self):
        # back to a previous image file
        self.save_file_num -= 1

        if self.save_file_num == -1:
            self.save_file_num = 0

        # update contents of Entry
        self.message.delete(0, END)
        self.message.insert(END, ' '.join(["Next save-name is:", self.get_save_im_path()]))
        # update saving param entries
        self.update_saving_param_entries()
    # <<< button functions ---------------


    # >>> slider functions ---------------
    def onSliderLeft(self, args):
        # change line
        self.canvas.delete("left_line")
        self.canvas.create_line(
            self.left.get(), 0, self.left.get(),
            self.my_images[self.my_image_number].height(), tag="left_line", fill='green')

    def onSliderRight(self, args):
        # change line
        self.canvas.delete("right_line")
        self.canvas.create_line(
            self.right.get(), 0, self.right.get(),
            self.my_images[self.my_image_number].height(), tag="right_line", fill='red')

    def onSliderTop(self, args):
        # change line
        self.canvas.delete("top_line")
        self.canvas.create_line(0, self.top.get(),
                                self.my_images[self.my_image_number].width(),
                                self.top.get(), tag="top_line", fill='green')

    def onSliderBottom(self, args):
        # change line
        self.canvas.delete("bottom_line")
        self.canvas.create_line(0, self.bottom.get(),
                                self.my_images[self.my_image_number].width(),
                                self.bottom.get(), tag="bottom_line", fill='red')
    # <<< slider functions ---------------


    # >>> button functions about saving ---------------
    # setting saving number from entry
    def onSavingNumSetButton(self):
        # get entry contents
        entry_str = self.saving_num_entry.get()
        try:
            entry_int = int(entry_str)
        except Exception as e:
            print('\n>>> [Error] Incorrect input: "{}"'.format(entry_str))
            print(e)
            # delete and insert
            self.saving_num_entry.delete(0, END)
            self.saving_num_entry.insert(END, str(self.save_file_num + 1))
            return False
        # change param
        self.save_file_num = entry_int - 1
        # update contents of Entry
        self.message.delete(0, END)
        self.message.insert(END, ' '.join(["Next save-name is", self.get_save_im_path()]))
        return True

    # setting saving base name from entry
    def onSvingBNamSetButton(self):
        # get entry contents
        entry_str = self.s_base_name_entry.get()
        if entry_str == '':
            print('\n>>> [Error] Incorrect input: "{}"'.format(entry_str))
            # insert
            self.s_base_name_entry.insert(END, self.save_base_name)
            return False
        # change param
        self.save_base_name = entry_str
        # update contents of Entry
        self.message.delete(0, END)
        self.message.insert(END, ' '.join(["Next save-name is", self.get_save_im_path()]))
        return True
    # <<< button functions about saving ---------------


    # >>> button functions (left, right, top, bottom) ---------------
    def onLRTB_Button(self, mode):
        def onLRTB_Nest():
            #print('\n -> [Func] onLRTB_Button: mode="{}"'.format(mode))
            if mode == 'L+':
                # left slider plus(+) mode
                # change line
                self.canvas.delete("left_line")
                update_num = self.left.get() + 1
                if update_num > self.my_images[self.my_image_number].width():
                    update_num = self.my_images[self.my_image_number].width()
                self.canvas.create_line(
                    update_num, 0, update_num,
                    self.my_images[self.my_image_number].height(), tag="left_line", fill='green')
                # set slider
                self.left.set(update_num)
                return True
            elif mode == 'L-':
                # left slider minus(-) mode
                # change line
                self.canvas.delete("left_line")
                update_num = self.left.get() - 1
                if update_num < 0:
                    update_num = 0
                self.canvas.create_line(
                    update_num, 0, update_num,
                    self.my_images[self.my_image_number].height(), tag="left_line", fill='green')
                # set slider
                self.left.set(update_num)
                return True
            elif mode == 'R+':
                # right slider plus(+) mode
                # change line
                self.canvas.delete("right_line")
                update_num = self.right.get() + 1
                if update_num > self.my_images[self.my_image_number].width():
                    update_num = self.my_images[self.my_image_number].width()
                self.canvas.create_line(
                    update_num, 0, update_num,
                    self.my_images[self.my_image_number].height(), tag="right_line", fill='red')
                # set slider
                self.right.set(update_num)
                return True
            elif mode == 'R-':
                # right slider minus(-) mode
                # change line
                self.canvas.delete("right_line")
                update_num = self.right.get() - 1
                if update_num < 0:
                    update_num = 0
                self.canvas.create_line(
                    update_num, 0, update_num,
                    self.my_images[self.my_image_number].height(), tag="right_line", fill='red')
                # set slider
                self.right.set(update_num)
                return True
            elif mode == 'T+':
                # top slider plus(+) mode
                # change line
                self.canvas.delete("top_line")
                update_num = self.top.get() + 1
                if update_num > self.my_images[self.my_image_number].height():
                    update_num = self.my_images[self.my_image_number].height()
                self.canvas.create_line(0, update_num,
                                        self.my_images[self.my_image_number].width(),
                                        update_num, tag="top_line", fill='green')
                # set slider
                self.top.set(update_num)
                return True
            elif mode == 'T-':
                # top slider minus(+) mode
                # change line
                self.canvas.delete("top_line")
                update_num = self.top.get() - 1
                if update_num < 0:
                    update_num = 0
                self.canvas.create_line(0, update_num,
                                        self.my_images[self.my_image_number].width(),
                                        update_num, tag="top_line", fill='green')
                # set slider
                self.top.set(update_num)
                return True
            elif mode == 'B+':
                # bottom slider plus(+) mode
                # change line
                self.canvas.delete("bottom_line")
                update_num = self.bottom.get() + 1
                if update_num > self.my_images[self.my_image_number].height():
                    update_num = self.my_images[self.my_image_number].height()
                self.canvas.create_line(0, update_num,
                                        self.my_images[self.my_image_number].width(),
                                        update_num, tag="bottom_line", fill='red')
                # set slider
                self.bottom.set(update_num)
                return True
            elif mode == 'B-':
                # bottom slider minus(-) mode
                # change line
                self.canvas.delete("bottom_line")
                update_num = self.bottom.get() - 1
                if update_num < 0:
                    update_num = 0
                self.canvas.create_line(0, update_num,
                                        self.my_images[self.my_image_number].width(),
                                        update_num, tag="bottom_line", fill='red')
                # set slider
                self.bottom.set(update_num)
                return True
            else:
                # unknown mode
                print('\n>>> [Error] Unknown mode: {}'.format(mode))
                return False
        # return function object
        return onLRTB_Nest
    # <<< button functions (left, right, top, bottom) ---------------


    # >>> path functions ---------------
    # get image file path
    def filenameMaker(self, number):
        return self.my_img_paths[number]

    # get saved image file name
    def get_save_im_path(self):
        return os.path.join(CR_IM_DIR,
                ''.join([self.save_base_name,
                         str(self.save_file_num + 1).zfill(len(str(self.im_num * 10)) ),
                         ''.join([os.extsep, 'jpg'])
                ]) )
    # <<< path functions ---------------


    # >>> update functions ---------------
    # update sliders
    def update_sliders(self):
        # update slider for cropping a image
        self.left.configure(to=self.my_images[self.my_image_number].width())
        self.right.configure(to=self.my_images[self.my_image_number].width())
        self.top.configure(to=self.my_images[self.my_image_number].height())
        self.bottom.configure(to=self.my_images[self.my_image_number].height())
        # moving with adjusting a image displaying a line for cropping a image
        self.left.set(0)
        self.right.set(self.my_images[self.my_image_number].width())
        self.top.set(0)
        self.bottom.set(self.my_images[self.my_image_number].height())

    # update saving param entry
    def update_saving_param_entries(self):
        # --- delete and insert
        # saving num
        self.saving_num_entry.delete(0, END)
        self.saving_num_entry.insert(END, str(self.save_file_num + 1))
        # saving base name
        self.s_base_name_entry.delete(0, END)
        self.s_base_name_entry.insert(END, self.save_base_name)

    # update slider line
    def update_lines(self):
        # --- change lines
        # right line
        self.canvas.delete("right_line")
        self.canvas.create_line(
            self.right.get(), 0, self.right.get(),
            self.my_images[self.my_image_number].height(), tag="right_line", fill='red')
        # top line
        self.canvas.delete("top_line")
        self.canvas.create_line(0, self.top.get(),
                                self.my_images[self.my_image_number].width(),
                                self.top.get(), tag="top_line", fill='green')
        # bottom line
        self.canvas.delete("bottom_line")
        self.canvas.create_line(0, self.bottom.get(),
                                self.my_images[self.my_image_number].width(),
                                self.bottom.get(), tag="bottom_line", fill='red')
    # <<< update functions ---------------
# <<< class MainWindow ----------------------------------------------------------------------



# main function
def main():
    root = Tk()
    MainWindow(root)
    root.mainloop()



# calling  main funcion
if __name__ == '__main__':
    main()
