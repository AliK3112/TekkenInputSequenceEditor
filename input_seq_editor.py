import tkinter as tk
from tkinter import Scrollbar, filedialog, Text, Listbox
import os
import json
from tkinter.constants import ACTIVE, SINGLE

root = tk.Tk()
root.title("TEKKEN Input Sequence Viewer")

commandLabels = {}


class Input_Sequence:
    def __init__(self, frames=0, inputs=0, u3=0, index=-1):
        self.frames = frames
        self.inputs = inputs
        self.u3 = u3
        self.ext_idx = index
        return self


class Input_Extradata:
    def __init__(self, index=-1, direction=0, command=0):
        self.index = index
        self.direction = direction
        self.command = command
        return self


def getCommandStr(commandBytes):
    inputs = ""
    direction = ""

    inputBits = commandBytes >> 32
    directionBits = commandBytes & 0xffffffff

    # for i in range(9, 12):
    #     if inputBits & (1 << (i)):
    #         if inputs == "":
    #             inputs += " Hold %d" % (i-8)
    #         else:
    #             inputs += "+%d" % (i-8)

    if inputBits & (1 << 4):
        inputs += "+RA"  # Label for Rage Art button

    for i in range(1, 5):
        if inputBits & (1 << (i - 1)):
            inputs += "+%d" % (i)

    if directionBits in commandLabels:
        direction = '(%s)' % commandLabels[directionBits]
    elif 32781 <= directionBits <= 36863:
        direction = " input_sequence[%d]" % (directionBits - 32781)
    else:
        direction = {
            (0): "",
            (1 << 1): "D/B",
            (1 << 2): "D",
            (1 << 3): "D/F",
            (1 << 4): "B",
            (1 << 5): "N",
            (1 << 6): "F",
            (1 << 7): "U/B",
            (1 << 8): "U",
            (1 << 9): "U/F",
            (1 << 15): "[AUTO]",
            (32769): " Double tap F",
            (32770): " Double tap B",
            (32771): " Double tap U",
            (32772): " Double tap D",
        }.get(directionBits, "UNKNOWN")

    if direction == "" and inputs != "":
        return inputs[1:]
    if inputBits >> 29 == 1:
        return "PARTIAL " + direction + inputs
    return direction + inputs


def LoadLabels():
    try:
        with open("./editorCommands.txt", "r") as f:
            for line in f:
                commaPos = line.find(',')
                val, label = line[:commaPos], line[commaPos + 1:].strip()
                commandLabels[int(val, 16)] = label
    except:
        pass


def LoadJSON(filename):
    try:
        with open(filename) as f:
            global data
            data = json.load(f)
    except FileNotFoundError:
        data = None
    return data


def PopulateList(list):
    frame1.delete(0, "end")
    counter = 0
    for i in list:
        frame1.insert("end", ("%4d - Frames: %7d | Inputs: %7d | Extraindex: %4d" %
                      (counter, i["u1"], i["u2"], i["extradata_idx"])))
        counter += 1


def addApp():
    for widgets in frame0.winfo_children():
        widgets.destroy()
    filename = filedialog.askopenfilename(
        initialdir="./", title="Select JSON file", filetypes=[("Json File", "*.json")])
    data = LoadJSON(filename)
    label = tk.Label(frame0, text=data["character_name"], bg="#8ca4e7")
    label.pack()
    global input_sequences
    input_sequences = data["input_sequences"]
    PopulateList(input_sequences)
    return


canvas = tk.Canvas(root, height=500, width=700, bg="#263D42")
canvas.pack()


frame1 = tk.Listbox(root, bg="white", selectmode=SINGLE)
frame1.place(relwidth=0.5, relheight=0.8, rely=0.1)

scrollbar = Scrollbar(frame1)
scrollbar.pack(side="right", fill="both")
frame1.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=frame1.yview)

frame2 = tk.Listbox(root, bg="#d8dce6", selectmode=SINGLE)
frame2.place(relwidth=0.5, relheight=0.8, relx=0.5, rely=0.1)

frame0 = tk.Frame(root, bg="#e4bdba")
frame0.place(relwidth=1, relheight=0.1)

label = tk.Label(frame0, text=None, bg="#e4bdba")
label.pack()

openFile = tk.Button(root, text="Open File", padx=10,
                     pady=5, fg="white", bg="#263D42", command=addApp)
openFile.pack()


def CurSelect(evt):
    ind = frame1.curselection()
    frames = input_sequences[ind[0]]["u1"]
    ninputs = input_sequences[ind[0]]["u2"]
    index = input_sequences[ind[0]]["extradata_idx"]
    # print(frames, ninputs, index)
    input_extra = data["input_extradata"]
    inputs = input_extra[index:index+ninputs]
    frame2.delete(0, "end")
    # print(inputs)
    for i in inputs:
        directions = i["u1"]
        buttons = i["u2"]
        result = (buttons << 32) + directions
        val = ("%08x %08x - %s" % (buttons, directions, getCommandStr(result)))
        # val = ("%016x - %s" % (result, getCommandStr(result)))
        frame2.insert("end", val)
    # print(val)


def PressDown():
    ind = frame1.curselection()
    if ind < len(input_sequences)-1:
        frame1.select_anchor(ind)
        ind += 1
        frame1.select_set(ind)


def PressUp():
    ind = frame1.curselection()
    if ind > 0:
        frame1.select_clear(ind)
        ind -= 1
        frame1.select_set(ind)


frame1.bind('<<ListboxSelect>>', CurSelect)
frame1.bind('<<Down>>', lambda frame1: print(frame1.curselection()))
frame1.bind('<<Up>>', lambda frame1: print(frame1.curselection()))
LoadLabels()
root.mainloop()
