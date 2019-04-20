import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
import os
import time
import threading
import mss
from datetime import datetime
from LockinAmp import lockinAmp
from keithley2400 import Keithley2400
from keithley import Keithley
from PIL import Image

root = Tk()
root.title('Hz Simple MOKE')

global scan_field_output, measured_values, dataplot, sens_lbl, x1, y1, x2, y2

fig = plt.Figure(figsize=(6,5), dpi=100)
ax = fig.add_subplot(111)
scan_field_output = []
measured_values = []
sens_lbl = ['']

x1=1086
y1=350
x2=1206
y2=428

def click(root2):
    print("X1: %d, Y1: %d" %(root2.winfo_x(), root2.winfo_y()))
    print("X2: %d, Y2: %d\n" %(root2.winfo_x()+root2.winfo_width(), root2.winfo_y()+root2.winfo_height()))
    global y1
    global x2
    global y2
    global x1
    x1 = root2.winfo_x()
    y1 = root2.winfo_y()
    x2 = root2.winfo_x()+root2.winfo_width()
    y2 = root2.winfo_y()+root2.winfo_height()

def perfSettings():

    perfFrame = Tk()

    perfFrame.title("Determine Capture Area Coordinates")
    perfFrame.configure(bg='#F2F2F2')
    perfFrame.geometry("200x150")

    btn = ttk.Button(master=perfFrame, text='box', command = lambda : click(perfFrame), width=10)
    btn.pack()
    perfFrame.protocol('WM_DELETE_WINDOW', quit) 
    perfFrame.mainloop()


screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

def main():

    # plot labels
    plot_title = "Realtime MOKE Signal vs H Plot"
    x_lbl = "Applied Field (Oe)"
    y_lbl = "Realtime MOKE Signal (R+B+G)"

    # dictionaries of GUI contents
    # default initial values
    mag_dict = {
                'Hz Field (Oe)': 100,
                'Hz Step (Oe)': 5,
                'Output Time (s)': 1
                }

    # default values required for initializing lockin via Pyvisa
    lockin_dict = {'Mode': '1st', # Set a default mode (1st or 2nd)
                'Sensitivity': '10mV', # Set a default sensitivity range (mV or uV)
                'Signal Voltage (V)': 1, # Set a default OSC signal voltage (V)
                'Frequency (Hz)': 1171 # Set a default OSC frequency (Hz)
                }

    # values set by various functions, define measurement settings
    control_dict = {
                    'H Output Direction': 'Hz', # set with make_buttons()
                    'Hz DAC Channel': 1, # displayed in make_extras()
                    'Hz/DAC (Oe/V)': 1029.5, # displayed in make_extras()
                    'Hz DAC Limit': 0.25, # Voltage limit of X direction mag
                    'Display': '', # set with make_info()
                    'File Name': 'Sample Name', # set with make_extras(), used in save function
                    'Directory': ''# set with set_directory(), updated with change_directory()
                    }


    # frames for various widgets
    content = Frame(root)
    plt_frame = Frame(content, borderwidth=10, relief="sunken")
    settings_frame = Frame(content, borderwidth=5)
    information_frame = Frame(content, borderwidth=5)
    buttons_frame = Frame(content, borderwidth=5)
    rows =20

    # grid of above frames
    content.grid(column=0, row=0, sticky='nsew')
    plt_frame.grid(column=0, row=0, columnspan=3, rowspan=rows, sticky='nsew')
    settings_frame.grid(column=3, row=0, columnspan=2, rowspan=rows, sticky='nsew')
    information_frame.grid(column=0, row=rows, columnspan=3, sticky='nsew')
    buttons_frame.grid(column=3, row=rows, columnspan=2, sticky='nsew')

    control_dict['Display'] = make_info(information_frame)
    mag_dict = make_form(settings_frame, mag_dict, 'Magnetic Settings')
    make_extras(settings_frame, mag_dict, control_dict)
    make_plot(plt_frame, plot_title, x_lbl, y_lbl)
    make_buttons(buttons_frame, mag_dict, control_dict, plot_title, x_lbl, y_lbl, lockin_dict)

    #weights columns for all multiple weight=1 columns
    weight(buttons_frame)
    weight(information_frame)
    weight(settings_frame)

    # weights for all rows and columns with weight!=1
    content.columnconfigure(0, weight=3)
    content.columnconfigure(1, weight=3)
    content.columnconfigure(2, weight=3)
    content.columnconfigure(3, weight=1)
    content.columnconfigure(4, weight=1)
    content.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    plt_frame.columnconfigure(0, weight=1)
    plt_frame.rowconfigure(0, weight=1)   
    information_frame.columnconfigure(3, weight=0) # necessary to keep the scroll bar tiny
    information_frame.rowconfigure(0, weight=1)    
    buttons_frame.rowconfigure(0, weight=1)
    #--------end of GUI settings-----------#

    # sets current directory to default (~/Documents/Measurements)
    control_dict['Directory'] = set_directory(control_dict['Display'])

    ani = animation.FuncAnimation(fig, animate, interval=200, fargs=[plot_title, x_lbl, y_lbl])

    root.protocol('WM_DELETE_WINDOW', quit) 

    th2 = threading.Thread(target=perfSettings)
    th2.daemon = True
    th2.start()
    root.mainloop()
#----------------------------------------END OF MAIN-------------------------------------------#


# animation to plot data
def animate(i, title, x, y):
    global scan_field_output, measured_values, sens_lbl

    ax.clear()
    ax.grid(True)
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    #ax.set_label(['Applied Current: %s (mA)\nFixed Field: %s (Oe)' %(curr_lbl[0], fix_lbl[0])])
    ax.plot(scan_field_output[0:len(measured_values)], measured_values,'b-o', ms=10, mew=0.5)


# takes a given frame and gives all columns a weight of 1
def weight(frame):

    for x in range(frame.grid_size()[0]):
        frame.columnconfigure(x, weight=1)


# takes a dictionary and makes labels and entry widgets for key/value pairs
# returns updated dictionary with entry values
def make_form(root, dictionary, frametxt):

    lf = LabelFrame(root, text=frametxt)
    lf.grid(ipadx=2, ipady=2, sticky='nsew')
    for counter, x in enumerate(dictionary.items()):
        lab = Label(lf, width=20, text=x[0], anchor='w')
        ent = Entry(lf, width=20); ent.insert(0, str(x[1]))
        lab.grid(row=counter, column=0, sticky='nsew')
        ent.grid(row=counter, column=1, sticky='nsew')
        dictionary[x[0]] = ent # set dictionary value to entry widget

    return dictionary


# initializes and grids matplotlib plot 
def make_plot(root, title, x_label, y_label):

    global dataplot

    # canvas for matplotlib gui
    dataplot = FigureCanvasTkAgg(fig, root)
    dataplot.draw()
    dataplot.get_tk_widget().grid(row=0, column=0, pady=0, padx=0, sticky='nsew')


# creates and grids the listbox and scroll bar
def make_info(root):

    listbox = Listbox(root, height=5)
    y_scroll = Scrollbar(root, orient=VERTICAL, command=listbox.yview)
    listbox['yscrollcommand'] = y_scroll.set
    listbox.grid(column=0, row=0, columnspan=3, sticky='nsew')
    y_scroll.grid(column=3, row=0, sticky='ns')

    return listbox



# extra radio buttons and selectors
def make_extras(root, mag_dict, control_dict):

    lf = LabelFrame(root, text='Measurement Options')
    lf.grid(ipadx=2, ipady=2, sticky='nsew')

    # lockin DAC labels
    Hz_lbl = Label(lf, width=20, text=('Hx DAC: %s' % control_dict['Hz DAC Channel']), anchor='w')
    Hz_conv_lbl = Label(lf, width=20, text=('Hx DAC: %s' % control_dict['Hz/DAC (Oe/V)']), anchor='w')
    
    # labels for DAC channels and conversion values, now only editable back end.
    Hz_lbl.grid(row=2, column=0, sticky='nsew')
    Hz_conv_lbl.grid(row=2, column=1, sticky='nsew')

    # file name label and entry
    file_lab = Label(lf, width=20, text='File Name', anchor='w')
    file_ent = Entry(lf, width=20); file_ent.insert(0, control_dict['File Name'])
    file_lab.grid(row=3, column=0, sticky='nsew')
    file_ent.grid(row=3, column=1, sticky='nsew')
    control_dict['File Name'] = file_ent


# creates and grids buttons
def make_buttons(root, mag_dict, control_dict, plot_title, x_lbl, y_lbl, lockin_dict):

    control_dict['H Output Direction'] = StringVar(); control_dict['H Output Direction'].set('Hz')

    # button list
    measure_button = Button(root, text='Measure', \
        command=lambda:measure_method(mag_dict, control_dict, lockin_dict))
    dir_button = Button(root, text='Change Directory', \
        command=lambda:change_directory(control_dict, control_dict['Display']))
    quit_button = Button(root, text='Quit', \
        command=lambda:quit_method(control_dict['Display'], lockin_dict))
    clear_button = Button(root, text='Clear', \
        command=lambda:clear_method(plot_title, x_lbl, y_lbl, control_dict['Display']))
    output_button = Button(root, text='Output', \
        command=lambda:output_method(control_dict, mag_dict, lockin_dict))

    # grid buttons
    output_button.grid(row=0, column=0, columnspan=2, sticky='nsew')
    measure_button.grid(row=1, column =0, columnspan=2, sticky='nsew')
    clear_button.grid(row = 3, column = 0, columnspan=1, sticky='nsew')
    dir_button.grid(row=2, column=0, columnspan=2, sticky='nsew')
    quit_button.grid(row=3, column=1, columnspan=1, sticky='nsew')


# does the matplotlib gui stuff to clear plot area
def plot_set(title, x_label, y_label):

    ax.clear()
    ax.grid(True)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.axis([-1, 1, -1, 1]) 


# sets default save directory, returns directory path
def set_directory(display):

    test = os.path.expanduser('~/Documents')

    if os.path.isdir(test + '/Measurements'):
        os.chdir(test + '/Measurements')
    else:
        os.mkdir(test + '/Measurements')
        os.chdir(test + '/Measurements')

    cur_dir = os.getcwd()

    display.insert('end', 'The current directory is set to: %s' % cur_dir)
    display.see(END)

    return cur_dir


# changes the save directory
def change_directory(control_dict, display):

    control_dict['Directory'] = filedialog.askdirectory()
    display.insert('end', control_dict['Directory'])
    display.see(END)


# applies a field H in the given direction at a given strength
def output_method(control_dict, mag_dict, lockin_dict):
    display = control_dict['Display']
    amp = lockinAmp(lockin_dict['Mode'], lockin_dict['Sensitivity'], lockin_dict['Signal Voltage (V)'], lockin_dict['Frequency (Hz)'])
    t = mag_dict['Output Time (s)'].get() # output time
    output = mag_dict['Hz Field (Oe)'].get() # output value
    interval = control_dict['Hz/DAC (Oe/V)'] # conversion integral

    # confirms output is number
    if output.lstrip('-').replace('.','',1).isdigit():
        # if output below threshold value, then have lockin amp output for t seconds
        if float(output) / float(interval) < float(control_dict['Hz DAC Limit']):
            amp.dacOutput((float(output) / float(interval)), control_dict['Hz DAC Channel'])
            time.sleep(float(t))
            amp.dacOutput(0, control_dict['Hz DAC Channel'])
            display.insert('end', 'Hx output for %s second(s)' % t)
            display.see(END)
        else:
            messagebox.showwarning('Output Too Large', 'Output value beyond amp voltage threshold')
            display.insert('end', 'Output value too large!')
            display.see(END)
    else:
        messagebox.showwarning('Invalid Entry', 'Output or conversion factor not recognized as a number.')


# clears and redraws the matplotlib gui
def clear_method(title, x_label, y_label, display):

    plot_set(title, x_label, y_label)
    dataplot.show()
    display.delete(0, END)
    print("clear all")


# turns off all outputs and then quits the program
def quit_method(display, lockin_dict):

    global root

    q = messagebox.askquestion('Quit', 'Are you sure you want to quit?')

    if q == 'yes':
        amp = lockinAmp(lockin_dict['Mode'], lockin_dict['Sensitivity'], lockin_dict['Signal Voltage (V)'], lockin_dict['Frequency (Hz)'])
        amp.dacOutput(0, 1)
        amp.dacOutput(0, 2)
        amp.dacOutput(0, 3)
        amp.dacOutput(0, 4)
        display.insert('end', "All fields set to zero.")
        display.see(END)
        time.sleep(.1)

        root.quit()
    else:
        pass


# takes maximum value and step size and creates a list of all values (floats) to run from low to high
def make_list(max_val, step_val):
    # checks to make sure inputs are valid (numbers)
    if max_val.lstrip('-').replace('.','',1).isdigit() and step_val.lstrip('-').replace('.','',1).isdigit():
        maximum = float(max_val)
        step = float(step_val)
        new_list = []
        # if step is zero, field is only measured at that value
        if step == 0.0:
            return [maximum]
        # if maximum is a positive value, build list from neg to positive
        elif maximum > 0.0:
            maximum = -maximum
            while maximum <= float(max_val):
                new_list.append(maximum)
                maximum += step
            return new_list
        # if maximum is a negative value, build the list
        else:
            while maximum <= -float(max_val):
                new_list.append(maximum)
                maximum += step
            return new_list
    else:
        messagebox.showwarning('Invalid Entry', 'Field or step input is not a digit')


# takes file parameters and results and saves the file, should have 5 lines before data is saved
def save_method(x_values, y_values, display, directory, name):

    stamp = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    file = open(str(directory)+"/"+str(name)+"_Simple_MOKE_"+str(stamp), "w")
    file.write("Number"+" "+"Hx Field(Oe)"+" "+"MOKE Signal (A.U.)"+"\n")

    for counter, value in enumerate(y_values):
        file.write(str(counter)+" "+str(x_values[counter])+" "+str(value)+"\n")
        
    file.closed

    display.insert('end', stamp)
    display.insert('end', "The Measurement data is saved.")
    display.see(END)


# finds the luminosity of the bbox area
def imageMethodFAST(X1,Y1,X2,Y2):

    with mss.mss() as sct:
        monitor = {'top': Y1, 'left': X1, 'width': X2-X1, 'height': Y2-Y1}
        sct_img = sct.grab(monitor)
        image = Image.frombytes('RGB', sct_img.size, sct_img.rgb)

    width=image.size[0]
    height=image.size[1]

    R=0
    G=0
    B=0

    for x in range(width):
        for y in range(height):
            R+=image.getpixel((x, y))[0]
            G+=image.getpixel((x, y))[1]
            B+=image.getpixel((x, y))[2]

    R=R/(width*height)
    G=G/(width*height)
    B=B/(width*height)

    L=R+G+B
    return L


# takes the difference between to scan values and tells how long to rest
def charging(val):
    if val >= 2500:
        return 5.0
    elif 1500 <= val < 2500:
        return 3.0
    elif 1000 <= val < 1500:
        return 1.0
    elif 500 <= val < 1000:
        return 0.5
    elif 100 <= val < 500:
        return 0.25
    elif 50 <= val < 100:
        return 0.1
    else:
        return 0.05

# measurement loop, iterates over values of a list built from parameters in dictionaries
def measure_method(mag_dict, control_dict, lockin_dict):
    
    display = control_dict['Display']

    # target of threading, allows for smooth running
    def measure_loop():
        global scan_field_output, measured_values, sens_lbl

        measured_values = []
        sens_lbl = ['']

        # builds list from step and max value
        scan_field_output = make_list(mag_dict['Hz Field (Oe)'].get(), mag_dict['Hz Step (Oe)'].get())
        # take inverse list and add it on, creating the full list values to measure at
        inverse = reversed(scan_field_output[0:-1])
        scan_field_output += inverse


        # ensures output voltages will not exceed amp thresholds
        if max(scan_field_output) / float(control_dict['Hz/DAC (Oe/V)']) < float(control_dict['Hz DAC Limit']):
            
            # initialize machines
            amp = lockinAmp(lockin_dict['Mode'], lockin_dict['Sensitivity'], lockin_dict['Signal Voltage (V)'], lockin_dict['Frequency (Hz)'])

            # intializes the measurement data list
            measured_values = []

            # measurement loops -  measure pos and neg current at give scan value and take avg abs val (ohms)
            for counter, scan_val in enumerate(scan_field_output):

                if counter == 0:
                    diff = abs(scan_val)
                else:
                    diff = abs(scan_val - scan_field_output[counter-1])
                amp.dacOutput((scan_val / float(control_dict['Hz/DAC (Oe/V)'])), control_dict['Hz DAC Channel'])
                time.sleep(charging(diff))
                tmp = imageMethodFAST(x1, y1, x2, y2) # get image luminosity
                measured_values.append(tmp)
                display.insert('end', 'Applied Hz Field Value: %s (Oe)      MOKE Signal: %s (A.U.)' %(scan_val, tmp))
                display.see(END)

            # save data
            save_method(scan_field_output, measured_values, display, control_dict['Directory'], control_dict['File Name'].get())

            # turn everything off at end of loop
            amp.dacOutput(0, control_dict['Hz DAC Channel'])

            display.insert('end',"Measurement finished")
            display.see(END)
        else:
            messagebox.showwarning('Output Too Large', 'Output value beyond amp voltage threshold')
            display.insert('end', 'Output value too large!')
            display.see(END)

        #----------------------------END measure_loop----------------------------------#

    # Only one measurement thread allowed. This is a cheap and easy workaround so we don't have to stop threads
    if threading.active_count() == 2:
        # thread is set to Daemon so if mainthread is quit, it dies
        t = threading.Thread(target=measure_loop, name='measure_thread', daemon=True)
        t.start()
    else:
        messagebox.showerror('Error', 'Multiple threads detected!')


if __name__ == '__main__':
    main()