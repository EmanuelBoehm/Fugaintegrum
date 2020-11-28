import tkinter as tk
import numpy as np
from PIL import Image, ImageTk

root = tk.Tk()

array = np.ones((40,40))*150
img =  ImageTk.PhotoImage(image=Image.fromarray(array))

canvas = tk.Canvas(root,width=300,height=300)
canvas.pack()
canvas.create_image(20,20, anchor="nw", image=img)

root.mainloop()