import tkinter as tk
from tkinter import Event, Scrollbar, filedialog, Text, Listbox
import re
import json
from typing import Sequence

root = tk.Tk()
root.title("TEKKEN Input Sequence Viewer")

commandLabels = {}


class Input_Sequence:
    def __init__(self, frames=0, inputs=0, u3=0, ext_idx=-1):
        self.frames = frames
        self.inputs = inputs
        self.u3 = u3
        self.ext_idx = ext_idx

    def print(self):
        print(
            f"Frames: {self.frames} | Inputs: {self.inputs} | ExtIndex: {self.ext_idx}")


def print_input_sequences(seq_list):
    for seq in seq_list:
        seq.print()


class Input_Extradata:
    def __init__(self, index=-1, direction=0, command=0):
        self.index = index
        self.direction = direction
        self.command = command


def getDirectionalinput(directionBytes):
    value = ""
    if (directionBytes & (1 << 1)):
        value += "| D/B "
    if (directionBytes & (1 << 2)):
        value += "| D "
    if (directionBytes & (1 << 3)):
        value += "| D/F "
    if (directionBytes & (1 << 4)):
        value += "| B "
    if (directionBytes & (1 << 5)):
        value += "| N "
    if (directionBytes & (1 << 6)):
        value += "| F "
    if (directionBytes & (1 << 7)):
        value += "| U/B "
    if (directionBytes & (1 << 8)):
        value += "| U "
    if (directionBytes & (1 << 9)):
        value += "| U/F "
    if (directionBytes & (1 << 10)):
        value += "| UNK "

    # Checking if command has more than 1 inputs
    if (len(value) > 6):
        return "(%s)" % value[2:-1]
    # elif (len(value) == 0):
    #     return "UNKNOWN"
    return value[1:]


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

    if directionBits < 0x8000:
        direction = getDirectionalinput(directionBits)
    elif directionBits < 0x800d:
        direction = {
            (32768): "[AUTO]",
            (32769): " Double tap F",
            (32770): " Double tap B",
            (32771): " Double tap U",
            (32772): " Double tap D",
        }.get(directionBits, "UNKNOWN")
    elif directionBits <= 36863:
        direction = " input_sequence[%d]" % directionBits - 0x800d
    else:
        direction = "UNKNOWN"

        # if directionBits in commandLabels:
        #     direction = '(%s)' % commandLabels[directionBits]
        # else:
        #     direction = {
        #         (0): "",
        #         (1 << 1): "D/B",
        #         (1 << 2): "D",
        #         (1 << 3): "D/F",
        #         (1 << 4): "B",
        #         (1 << 5): "N",
        #         (1 << 6): "F",
        #         (1 << 7): "U/B",
        #         (1 << 8): "U",
        #         (1 << 9): "U/F",
        #         (1 << 15): "[AUTO]",
        #         (32769): " Double tap F",
        #         (32770): " Double tap B",
        #         (32771): " Double tap U",
        #         (32772): " Double tap D",
        #     }.get(directionBits, "UNKNOWN")
    # direction = getDirectionalinput(directionBits)
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
    obj_list = []
    frame1.delete(0, "end")
    counter = 0
    for i in list:
        seq = Input_Sequence(i["u1"], i["u2"], i["u3"], i["extradata_idx"])
        frame1.insert("end", ("%4d - Frames: %7d | Inputs: %7d | Extraindex: %4d" %
                      (counter, i["u1"], i["u2"], i["extradata_idx"])))
        obj_list.append(seq)
        counter += 1
    # print_input_sequences(obj_list)


def addApp():
    for widgets in frame0.winfo_children():
        widgets.destroy()
    #
    filename = filedialog.askopenfilename(
        initialdir="./", title="Select JSON file", filetypes=[("Json File", "*.json")])
    if filename == "":
        return
    # Just for convenience
    # filename = "F:\My_Cheat_Tables\Scripts\TekkenInputSequenceEditor\\t7_DEVIL_JIN.json"
    data = LoadJSON(filename)
    label = tk.Label(frame0, text=data["character_name"], bg="#8ca4e7")
    label.pack()
    global input_sequences
    input_sequences = data["input_sequences"]
    PopulateList(input_sequences)
    return


canvas = tk.Canvas(root, height=500, width=700, bg="#263D42")
canvas.pack()


frame1 = tk.Listbox(root, bg="white", selectmode='single')
frame1.place(relwidth=0.5, relheight=0.8, rely=0.1)

scrollbar = Scrollbar(frame1)
scrollbar.pack(side="right", fill="both")
frame1.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=frame1.yview)

frame2 = tk.Listbox(root, bg="#d8dce6", selectmode='single')
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
    try:
        frames = input_sequences[ind[0]]["u1"]
        ninputs = input_sequences[ind[0]]["u2"]
        index = input_sequences[ind[0]]["extradata_idx"]
    except IndexError:  # Only occurs when I click an item from the other side
        print(f"Index Out of Range. Ind = {ind}")
        return
    seq = Input_Sequence(frames, ninputs, 0, index)
    # print(frames, ninputs, index)
    input_extra = data["input_extradata"]
    inputs = input_extra[index:index+ninputs]
    frame2.delete(0, "end")
    for widgets in frame2.winfo_children():
        widgets.destroy()
    # txtbox2 = tk.Text(frame2, height=1, width=20)
    # txtbox2.pack()
    # print(inputs)
    for i in inputs:
        directions = i["u1"]
        buttons = i["u2"]
        result = (buttons << 32) + directions
        miniframe = tk.Frame(frame2, height=2, width=40)
        label1 = tk.Label(miniframe, text=(
            "%s" % (getCommandStr(result))), width=20)
        label1.pack(side="left")
        txtbox1 = tk.Text(miniframe, height=1, width=20)
        # txtbox1.bind("<<Modified>>", ValueChanged)
        txtbox1.insert('insert', "%016x" % result)
        txtbox1.pack(side="left")
        sv = tk.StringVar()
        sv.trace("w", lambda name, index, mode, label=label1,
                 sv=sv: ValueChanged(sv, label))
        miniframe.pack()
        # val = ("%08x %08x - %s" % (buttons, directions, getCommandStr(result)))
        val = ("%s" % (getCommandStr(result)))
        # val = ("%016x - %s" % (result, getCommandStr(result)))
        # frame2.insert("end", val)
        # frame2.insert("end", txtbox1)
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


def ValueChanged(sv, label):
    value = sv.get()
    if value == "":
        label.text = ""
        return
    if re.match("^[0-9A-Fa-f]+$", value):
        label.text = getCommandStr(value)
    else:
        label.text = "INVALID"
    print("HELLO")
    return


frame1.bind('<<ListboxSelect>>', CurSelect)
frame1.bind('<<Down>>', lambda frame1: print(frame1.curselection()))
frame1.bind('<<Up>>', lambda frame1: print(frame1.curselection()))
LoadLabels()
root.mainloop()
