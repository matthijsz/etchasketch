from tkinter import filedialog
import tkinter, cv2
import PIL.Image, PIL.ImageTk
from Google_Image import *


def different_image(window):
    global Options_master
    Options_master['i'] += 1
    Google_Image_Get(Options_master['query'], Options_master['i'], Options_master['Directory'],
                     Options_master['safe_search'])
    Image_Transform('{0}/{1}.png'.format(Options_master['Directory'], Options_master['query']),
                    Options_master['threshold'])
    window.destroy()
    Image_window('{0}/{1}.png.mono.png'.format(Options_master['Directory'], Options_master['query']), True,
                 Options_master['threshold'])


def value_get(w, window, file, from_google):
    # global w
    global Options_master
    Options_master['threshold'] = int(w.get())
    Image_Transform(file, Options_master['threshold'])
    window.destroy()
    Image_window(file + '.mono.png', from_google, Options_master['threshold'])


def txt_callback(window, s1, var1):
    global Options_master
    if not var1.get():
        Options_master['safe_search'] = 'off'
    if ' ' in s1.get():
        Options_master['query'] = s1.get().replace(' ', '')
    else:
        Options_master['query'] = s1.get()
    window.destroy()


def menu_select(window, option):
    global Options_master
    Options_master['threshold'] = 100  # Default threshold
    if option == 'Google':
        window.destroy()
        Options_master['safe_search'] = 'active'
        root = tkinter.Tk()
        root.withdraw()
        Directory = tkinter.filedialog.askdirectory(parent=root, title='Please select a directory')
        Options_master['Directory'] = Directory
        root.destroy()
        Query_window()
        Options_master['i'] = 1  # Starting iterator to find images
        succes = Google_Image_Get(Options_master['query'], Options_master['i'], Options_master['Directory'],
                                  Options_master['safe_search'])
        if not succes:
            n = 0
            while (n < 5) and (not succes):
                Options_master['i'] += 1
                succes = Google_Image_Get(Options_master['query'], Options_master['i'], Options_master['Directory'],
                                          Options_master['safe_search'])
                n += 1
            if not succes:
                raise ImportError('Could not acces image')
        Image_Transform('{0}/{1}.png'.format(Options_master['Directory'], Options_master['query']),
                        Options_master['threshold'])
        Image_window('{0}/{1}.png.mono.png'.format(Options_master['Directory'], Options_master['query']), True,
                     Options_master['threshold'])
        var2 = Options_window()
        print(var2)
        Options_master['Targetfile'] = '{0}/{1}.png.mono.png'.format(Options_master['Directory'],
                                                                     Options_master['query'])
    else:
        window.destroy()
        root = tkinter.Tk()
        root.withdraw()
        File = tkinter.filedialog.askopenfile(parent=root, title='Choose your image')
        Options_master['File'] = str(File.name)
        Options_master['Directory'] = '/'.join(Options_master['File'].split('/')[:-1])
        root.destroy()
        Image_Transform(Options_master['File'], Options_master['threshold'])
        Image_window(Options_master['File'] + '.mono.png', False, Options_master['threshold'])
        var2 = Options_window()
        Options_master['Targetfile'] = Options_master['File'] + '.mono.png'
    if var2:
        Options_master['Print_process'] = True
    else:
        Options_master['Print_process'] = False


def Start_window():
    window = tkinter.Tk()
    window.title("Start path tracing")
    btn_Accept = tkinter.Button(window, text="Get image from Google", width=50,
                                command=lambda: menu_select(window, 'Google'))
    btn_Accept.pack(anchor=tkinter.CENTER, expand=True)
    btn_Accept = tkinter.Button(window, text="Use an existing file", width=50,
                                command=lambda: menu_select(window, 'File'))
    btn_Accept.pack(anchor=tkinter.CENTER, expand=True)
    # Starting pixel method may be implemented here still
    window.mainloop()


def Query_window():
    window = tkinter.Tk()
    window.title("Query input")
    s1 = tkinter.StringVar()
    e = tkinter.Entry(window, textvariable=s1)
    e.pack()
    e.delete(0, tkinter.END)
    e.insert(0, "your query here")
    var1 = tkinter.IntVar()
    c = tkinter.Checkbutton(window, text="Safe search", variable=var1)
    c.pack(anchor=tkinter.CENTER, expand=True)
    btn_Accept = tkinter.Button(window, text="Accept", width=50, command=lambda: txt_callback(window, s1, var1))
    btn_Accept.pack(anchor=tkinter.CENTER, expand=True)
    window.mainloop()


def Image_window(image_path, from_google, threshold):
    global Options_master
    # Create a window
    window = tkinter.Tk()
    window.title("Image adjustment")
    # Load an image using OpenCV
    cv_img = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
    height, width, no_channels = cv_img.shape
    canvas = tkinter.Canvas(window, width=width, height=height)
    canvas.pack()
    photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(cv_img))
    # Add a PhotoImage to the Canvas
    canvas.create_image(0, 0, image=photo, anchor=tkinter.NW)
    # Add buttons to perform functions
    if from_google:
        base_file = '{0}/{1}.png'.format(Options_master['Directory'], Options_master['query'])
        btn_Different = tkinter.Button(window, text="Get different image", width=50,
                                       command=lambda: different_image(window))
        btn_Different.pack(anchor=tkinter.CENTER, expand=True)
    else:
        base_file = Options_master['File']
    btn_Accept = tkinter.Button(window, text="Accept", width=50, command=window.destroy)
    btn_Accept.pack(anchor=tkinter.CENTER, expand=True)
    w = tkinter.Scale(window, from_=0, to=255, orient=tkinter.HORIZONTAL)
    w.set(threshold)
    w.pack(anchor=tkinter.CENTER, expand=True)
    btn_w = tkinter.Button(window, text="Change black/white cutoff", width=50,
                           command=lambda: value_get(w, window, base_file, from_google))
    btn_w.pack(anchor=tkinter.CENTER, expand=True)
    # Run the window loop
    window.mainloop()


def Options_window():
    window = tkinter.Tk()
    window.title("Options")
    save_images = tkinter.IntVar()
    c = tkinter.Checkbutton(window, text="Save images at every step", variable=save_images)
    c.pack(anchor=tkinter.CENTER, expand=True)
    btn_Accept = tkinter.Button(window, text="Accept", width=50, command=window.destroy)
    btn_Accept.pack(anchor=tkinter.CENTER, expand=True)
    window.mainloop()
    return save_images.get()


def tkinter_Run():
    global Options_master
    Options_master = {}
    Options_master['method'] = 'topleft'
    Start_window()
    return Options_master
