from PyQt4 import QtGui
import sys
# trick to change WM_CLASS to allow window manager to identify the plot window
if __name__ == '__main__':
    app = QtGui.QApplication(['Matplotlib'])

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time
import serial

ser = serial.Serial('/dev/ttyACM0', 9600, timeout=0)

x = []
y = []
# window left edge
wx = 0
# window length
w = 5

fig, ax = plt.subplots()
line, = ax.plot(x,y)
ax.set_ylim(0,1)
ax.set_xlim(wx,wx+w)
ax.grid(True)

def update(data):
    global x, y, wx
    x.extend(d[0] for d in data)
    y.extend(d[1] for d in data)
    if len(x) > 0 and x[-1] > wx+w:
        # update window
        wx = w*(x[-1]//w)
        # update data
        i = next(i[0] for i in enumerate(x) if i[1] > wx)
        if i > 0:
            i -= 1
        x = x[i:]
        y = y[i:]
        ax.set_xlim(wx,wx+w)
        #print(wx,wx+w)
        # compute average diff
        if len(x) > 1:
            d = sum(x[j+1]-x[j] for j in range(len(x)-1)) / (len(x)-1)
            #print(d)
    line.set_data(x,y)
    return line,

def clear():
    ser.flush()
    return line,

def read():
    # ugly buffering
    buf = b''
    while True:
        lines = ser.readall().split()
        if len(lines) > 0:
            lines[0] = buf + lines[0]
            buf = b''
            if not lines[-1].endswith(b')'):
                buf = lines[-1]
                lines = lines[:-1]
            if len(lines) > 0 and not lines[0].startswith(b'('):
                lines = lines[1:]
        tokens = [l[1:-1].split(b',') for l in lines]
        yield list((int(l[0])/1000,int(l[1])/1023) for l in tokens)

ani = animation.FuncAnimation(fig, update, read, clear, interval=25, blit=True)
plt.show()
