import json
from tkinter import *
from tkinter import filedialog


def LoadJSON(filename):
    try:
        with open(filename) as f:
            global data
            data = json.load(f)
    except FileNotFoundError:
        data = None
    return data


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
        value += "| UNKNOWN "

    # Checking if command has more than 1 inputs
    if (len(value) > 6):
        return "(%s)" % value[2:-1]
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

    if direction == "" and inputs != "":
        return inputs[1:]
    if (inputBits & (1 << 29)):
        return "PARTIAL " + direction + inputs
    return direction + inputs


class Input_Sequence:
    def __init__(self, frames=0, inputs=0, u3=0, ext_idx=-1):
        self.frames = frames
        self.inputs = inputs
        self.u3 = u3
        self.ext_idx = ext_idx
        # self.extradata = extradata

    def print(self):
        print(
            f"Frames: {self.frames} | Inputs: {self.inputs} | ExtIndex: {self.ext_idx}")

    def print_input_extradata(self):
        for seq in self.extradata:
            seq.print()


class Input_Extradata:
    def __init__(self, direction=0, command=0):
        # self.index = index
        self.direction = direction
        self.command = command

    def print(self):
        print("%.8x %.8x" % self.direction, self.command)
        return


class MainWindow:
    def __init__(self):
        # Setting Main Window Parameters
        self.root = Tk()
        self.root.title("TEKKEN Input Sequence Editor")
        self.root.minsize(800, 600)
        self.root.maxsize(1280, 720)
        self.root.geometry('800x600')
        self.root.iconbitmap("./myicon.ico")

        # Setting up menu bar
        self.menu = Menu(self.root)
        self.root.config(menu=self.menu)

        # Creating Menu Items
        self.menu1 = Menu(self.menu)
        self.menu2 = Menu(self.menu)

        # Adding those to main menu bar widget
        self.menu.add_cascade(label="New", menu=self.menu1)
        self.menu.add_cascade(label="Delete", menu=self.menu2)
        self.menu.add_cascade(label="Help", command=self.ShowHelpBox)

        # Adding commands into Menu 1
        self.menu1.add_command(label="Input Sequence", command=None)
        self.menu1.add_command(
            label="Duplicate Current Input Sequence", command=None)
        self.menu1.add_separator()
        self.menu1.add_command(label="Input Extradata", command=None)
        self.menu1.add_command(
            label="Duplicate Current Input Extradata List", command=None)

        # Adding commands into Menu 2
        self.menu2.add_command(label="Current Input Sequence", command=None)
        self.menu2.add_separator()
        self.menu2.add_command(label="Current Input Extradata", command=None)
        self.menu2.add_command(
            label="Current Input Extradata List", command=None)

        # Creating Header Widget. It stores app name
        self.filename_label = Label(self.root, text="NO FILE OPENED")
        self.filename_label.grid(row=0, column=0)

        # Creating Two main widgets (list boxes)
        self.inputSeqListFrame = Listbox(
            self.root, bg="white", selectmode='single', height=20, width=50)
        # self.inputSeqListFrame.grid(row=1, column=0)
        self.inputSeqListFrame.place(relwidth=0.5, relheight=0.8, rely=0.05)
        # Attaching Scrollbar to sequence frame list
        scrollbar = Scrollbar(self.inputSeqListFrame)
        scrollbar.pack(side="right", fill="both")
        self.inputSeqListFrame.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.inputSeqListFrame.yview)
        self.inputSeqListFrame.bind("<<ListboxSelect>>", self.sequenceSelected)

        self.inputExtradataListFrame = Listbox(
            self.root, bg="#d8dce6", selectmode='single', height=20, width=50)
        # self.inputExtradataListFrame.grid(row=2, column=0)
        self.inputExtradataListFrame.place(
            relwidth=0.5, relheight=0.8, relx=0.5, rely=0.05)

        # Creating & Placing the current editor
        self.currentInputSequenceEditor = self.CurrentInputSequenceEditor(
            self.root)

        # Creating "Open File" button & placing it
        self.openFileButton = Button(self.root, text="Open File", padx=10,
                                     pady=5, fg="white", bg="#263D42", command=self.OpenFile)
        # self.openFileButton.grid(row=600, column=0, padx=10)
        self.openFileButton.place(rely=0.94)

        # Setting Moveset Data
        self.movesetData = None
        self.inputSequence = None
        self.inputExtradata = None
        self.cancels = None
        self.groupCancels = None
        # self.newInputSequenceList = None
        return

    def ClearParameters(self):
        # TODO
        return

    def ShowHelpBox(self):
        # TODO
        print("HELP CLICKED!")
        return

    def sequenceSelected(self, event):
        ind = self.inputSeqListFrame.curselection()
        try:
            frames = self.inputSequence[ind[0]]["u1"]
            ninputs = self.inputSequence[ind[0]]["u2"]
            u3 = self.inputSequence[ind[0]]["u3"]
            index = self.inputSequence[ind[0]]["extradata_idx"]
        except IndexError:  # Only occurs when I click an item from the other side
            print(f"Index Out of Range. Ind = {ind}")
            return
        extradata_seqList = self.inputExtradata[index: ninputs + index]
        seq = Input_Sequence(frames, ninputs, u3, index)

        # Passing current sequence to the editor
        self.currentInputSequenceEditor.populate(seq)

        self.inputExtradataListFrame.delete(0, 'end')

        # Deleting all previous widgets
        for widgets in self.inputExtradataListFrame.winfo_children():
            widgets.destroy()

        for i in extradata_seqList:
            direction = i["u1"]
            buttons = i["u2"]
            result = (buttons << 32) + direction
            miniframe = Frame(self.inputExtradataListFrame, height=2, width=40)
            command = getCommandStr(result)
            label1 = Label(miniframe, text=(
                "%s" % command), width=20)
            label1.pack(side="left")
            txtbox1 = Text(miniframe, height=1, width=20)
            # txtbox1.bind("<<Modified>>", ValueChanged)
            txtbox1.insert('insert', "%0.16x" % result)
            txtbox1.pack(side="left")
            # sv = StringVar()
            # sv.trace("w", lambda name, index, mode, label=label1,
            #          sv=sv: ValueChanged(sv, label))
            miniframe.pack()
            # val = ("%08x %08x - %s" % (buttons, directions, getCommandStr(result)))
            val = ("%s" % command)
            # val = ("%016x - %s" % (result, getCommandStr(result)))
            # frame2.insert("end", val)
            # frame2.insert("end", txtbox1)
        return

    def OpenFile(self):
        self.filename = filedialog.askopenfilename(
            initialdir="./", title="Select JSON file", filetypes=[("Json File", "*.json")])
        if self.filename == "":
            return
        self.movesetData = LoadJSON(self.filename)
        self.filename_label.config(text=self.movesetData['character_name'])
        self.inputSequence = self.movesetData["input_sequences"]
        self.inputExtradata = self.movesetData["input_extradata"]
        self.cancels = self.movesetData["cancels"]
        self.groupCancels = self.movesetData["group_cancels"]
        self.PopulateList()
        return

    def PopulateList(self):
        # self.newInputSequenceList = []
        self.inputSeqListFrame.delete(0, "end")
        # extradata_seqList = None
        extidx = -1
        counter = 0
        for i in self.inputSequence:
            frames = i["u1"]
            ninputs = i["u2"]
            extidx = i["extradata_idx"]
            # extradata_seqList = self.inputExtradata[extidx: ninputs+extidx]
            seq = Input_Sequence(frames, ninputs, i["u3"],
                                 extidx)
            self.inputSeqListFrame.insert(
                "end", ("%4d - Frame Window: %7d | Inputs: %7d | Extraindex: %4d" % (counter, frames, ninputs, extidx)))
            # self.newInputSequenceList.append(seq)
            counter += 1
        return

    def main_loop(self):
        self.root.mainloop()

    class CurrentInputSequenceEditor:
        def __init__(self, parentroot):
            self.root = parentroot

            # Creating a frame
            self.Frame = Frame(self.root, height=3, borderwidth=3)

            # Inside this frame will be 3 text labels & text boxes
            self.u1_label = Label(self.Frame, text="Frame Window")
            self.u1_entry = Entry(self.Frame, width=20)
            self.u2_label = Label(self.Frame, text="Number of Inputs")
            self.u2_entry = Entry(self.Frame, width=20)
            self.idx_label = Label(self.Frame, text="Input Extradata Index")
            self.idx_entry = Entry(self.Frame, width=20)

            # Placing widgets inside frames
            self.u1_label.grid(row=0, column=0)
            self.u1_entry.grid(row=0, column=1)
            self.u2_label.grid(row=0, column=2)
            self.u2_entry.grid(row=0, column=3)
            self.idx_label.grid(row=0, column=4)
            self.idx_entry.grid(row=0, column=5)

            # Placing frame inside the parent window
            self.Frame.place(relwidth=0.8, relheight=0.2, rely=0.86)

        def populate(self, sequenceObj):
            self.u1_entry.delete(0, 'end')
            self.u2_entry.delete(0, 'end')
            self.idx_entry.delete(0, 'end')
            self.u1_entry.insert(0, sequenceObj.frames)
            self.u2_entry.insert(0, sequenceObj.inputs)
            self.idx_entry.insert(0, sequenceObj.ext_idx)
            return


def main():
    MainWindow().main_loop()
    return


if __name__ == "__main__":
    main()
