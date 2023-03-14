import PySimpleGUI as gui
from Functions import readFromPhoto, detectFromVideo, live
from Functions.databaseF import checkInDB, saveToDB, validateEditedPlate

"""
LAYOUTS
"""
def mainMenuLayout():
    return [
    [gui.Text("Izberi:", font=('Helvetica', 17))],
    [gui.Button('Beri iz slike v živo', key='-LIVE-', font=('Helvetica', 14))],
    [gui.Button('Beri iz slike', key='-IMAGE-', font=('Helvetica', 14))],
    [gui.Button('Beri iz videa', key='-VIDEO-', font=('Helvetica', 14))],
]

def chooseFileLayoutPhoto():
    return [
        [gui.Text("Izberi datoteko, ki jo želiš prebrati (pazi na tip)", font=('Helvetica', 13))],
        [gui.Input(key='-FILE-'), gui.FileBrowse()],
        [gui.Button("Submit")],
    ]
def chooseFileLayoutVideo():
    return [
        [gui.Text("Izberi datoteko, ki jo želiš prebrati (pazi na tip)", font=('Helvetica', 13))],
        [gui.Input(key='-FILE-', ), gui.FileBrowse(file_types=(("MP4 Files", "*.mp4"),))],
        [gui.Button("Submit")],
    ]

def editPlateLayoutQuestion(plate):
    return [
        [gui.Text(f"Ali želite spremeniti tablico {plate} pred shranjevanjem v bazo podatkov?", font=('Helvetica', 13))],
        [gui.Push(), gui.Button("Yes"), gui.Button("No"), gui.Push()]
    ]
def editPlateLayout(plate):
    return [
        [gui.Push(), gui.Text(f" {plate} ", text_color="red", font=('Helvetica bold', 16)), gui.Push()],
        [gui.Text("Vnesite urejeno tablico: ", font=('Helvetica', 13)), gui.Input(key="-EDITED_PLATE-")],
        [gui.Text("\t\tNaredite lahko največ 3 spremembe, brišete", font=('Helvetica', 9))],
        [gui.Text("\t\tlahko samo na koncu ter lahko spreminjate črke",font=('Helvetica', 9))],
        [gui.Push(), gui.Button("Potrdi"), gui.Button("Nazaj"), gui.Push()]
    ]

"""
SCREENS
"""

def mainMenu():
    window = gui.Window("License plate reader", mainMenuLayout())

    while True:
        event, values = window.read()
        if event == gui.WINDOW_CLOSED:
            break
        elif event == "-LIVE-":
            window.close()
            winLive()
        elif event == "-IMAGE-":
            window.close()
            winPhotoChoose()
        elif event == "-VIDEO-":
            window.close()
            winVideoChoose()

    window.close()
def winLive():
    readPlatesArray = live()
    if len(readPlatesArray) == 1:
        plate = readPlatesArray[0]
        if plate == "":
            displayNoPlatesRead()
        else:
            displayRecognizedPlate(plate)
    elif (len(readPlatesArray) is None) or (len(readPlatesArray) == 0):
        displayNoPlatesRead()
    else:
        displayRecognizedPlates(readPlatesArray)

    mainMenu()


def winPhotoChoose():
    window = gui.Window("License plate detection", chooseFileLayoutPhoto())

    while True:
        event, values = window.read()

        if event == gui.WINDOW_CLOSED:
            break
        elif event == "Submit":
            filePath = values['-FILE-']
            readPlatesArray = readFromPhoto(filePath)
            window.close()
            if len(readPlatesArray) == 1:
                plate = readPlatesArray[0]
                if plate == "":
                    displayNoPlatesRead()
                else:
                    displayRecognizedPlate(plate)
            elif (len(readPlatesArray) is None) or (len(readPlatesArray) == 0):
                displayNoPlatesRead()
            else:
                displayRecognizedPlates(readPlatesArray)
            break
    window.close()
    mainMenu()


def winVideoChoose():
    window = gui.Window("License plate detection", chooseFileLayoutVideo())

    while True:
        event, values = window.read()

        if event == gui.WINDOW_CLOSED:
            break
        elif event == "Submit":
            filePath = values['-FILE-']
            readPlatesArray = detectFromVideo(filePath)
            window.close()
            if len(readPlatesArray) == 1:
                plate = readPlatesArray[0]
                if plate == "":
                    displayNoPlatesRead()
                else:
                    displayRecognizedPlate(plate)
            elif (len(readPlatesArray) is None) or (len(readPlatesArray) == 0):
                displayNoPlatesRead()
            else:
                displayRecognizedPlates(readPlatesArray)
            break
    window.close()
    mainMenu()

def displayRecognizedPlates(platesArray):

    layout = [
        [gui.Text("Prepoznane tablice (najverjetnejše): ", font="helvetica, 12")]
    ]

    if len(platesArray) > 6:
        layout.extend([
            [gui.Listbox(values=platesArray, size=(30, 6))],

        ])
    else:
        layout.extend([
            [gui.Listbox(values=platesArray, size=(30, len(platesArray)), auto_size_text=True)]
        ])

    inDBarray = []

    for plate in platesArray:
        if checkInDB(plate):
            inDBarray.append(plate)

    layout.extend([
        [gui.Text("Tablice v bazi: ", font="helvetica, 12")],
    ])

    if len(inDBarray) > 6:
        layout.extend([
            [gui.Listbox(values=inDBarray, size=(30, 6))],
        ])
    else:
        layout.extend([
            [gui.Listbox(values=inDBarray, size=(30, len(inDBarray)), auto_size_text=True)]
        ])

    layout.extend([
        [gui.Text("Ali želite shraniti katero tablico?")],
        [gui.Push(), gui.Button("Yes"), gui.Button("No"), gui.Push()]
    ])

    window = gui.Window("Prepoznane tablice", layout)

    newArray = [x for x in platesArray if x not in inDBarray]

    while True:
        event, values = window.read()

        if event == gui.WINDOW_CLOSED:
            break
        elif event == "Yes":
            window.close()
            displaySelectPlatesToSave(newArray)
            break
        elif event == "No":
            break
    window.close()


def displayRecognizedPlate(plate):

    layout = [
        [gui.Text(f"Prepoznanana tablica: ", font="helvetica, 12"), gui.Text(f"{str(plate)}", font='Any 16 bold', text_color="red")],
    ]

    isIn = checkInDB(str(plate))

    if isIn:
        layout.extend([
            [gui.Text(f"Ta tablica je že vpisana v bazo podatkov.", font="helvetica, 12")],
            [gui.Push(), gui.Button("Next"), gui.Push()]
        ])
    else:
        layout.extend([
            [gui.Text("Tablica še ni v bazi. Ali jo želite shraniti?", font="helvetica, 12")],
            [gui.Push(), gui.Button('Yes'), gui.Button('No'), gui.Push()]
        ])

    window = gui.Window("Prepoznana tablica", layout)


    while True:
        event, values = window.read()

        if event == gui.WINDOW_CLOSED:
            break
        elif event == "Yes":
            window.hide()
            displayEditPlateQuestion(plate)
            break
        elif event =="No":
            break
        elif event == "Next":
            break
    window.close()

def displayNoPlatesRead():
    layout = [
        [gui.Text("Nismo zaznali nobenih tablic", font=("Helvetica, 18"))]
    ]

    window = gui.Window("Oh no", layout)

    while True:
        event, values = window.read()

        if event == gui.WINDOW_CLOSED:
            break
    window.close()

def displayEditPlate(plate):

    window = gui.Window("Do you?", editPlateLayout(plate))

    boolVal = False

    while True:
        event, values = window.Read()

        if event == gui.WINDOW_CLOSED:
            break
        elif event == "Potrdi":
            edited = values['-EDITED_PLATE-']
            succesful = validateEditedPlate(edited, plate)
            if succesful:
                suc = saveToDB(plate, edited)
                if suc:
                    window.close()
                    successSave()
                    break
                else:
                    window.close()
                    unsuccessSave()
                    break
            else:
                errorPlateEdit()
                suc = saveToDB(plate, plate)
                if suc:
                    window.close()
                    successSave()
                    break
                else:
                    window.close()
                    unsuccessSave()
                    break
        elif event == "Nazaj":
            boolVal = False
            break
    window.close()
    return boolVal

def displayEditPlateQuestion(plate):

    window = gui.Window("Do you?", editPlateLayoutQuestion(plate))

    while True:
        event, values = window.Read()

        if event ==  gui.WINDOW_CLOSED:
            break
        elif event == "Yes":
            window.hide()
            ch = displayEditPlate(plate)
            if not ch:
                break
            else:
                window.un_hide()
        elif event == "No":
            break
    window.close()

def displaySelectPlatesToSave(plateArray):

    layout = [
        [gui.Text("Tablice, katere je možno shranit:", font=("Helvetica, 13"))],
    ]

    if len(plateArray) > 8:
        layout.extend([
            [gui.Listbox(values=plateArray, size=(30, 8))],
        ])
    else:
        layout.extend([
            [gui.Listbox(values=plateArray, key="-SELECT-", size=(30, len(plateArray)), auto_size_text=True, select_mode='multiple', enable_events=True)]
        ])

    layout.extend([
        [gui.Text("Potrdite izbiro?", font=("Helvetica, 13"))],
        [gui.Push(), gui.Button('Yes'), gui.Button('No'), gui.Push()]
    ])

    window = gui.Window("Izbira tablic za shranit", layout)

    while True:
        event, values = window.Read()

        if event == gui.WINDOW_CLOSED:
            break
        elif event == "Yes":
            selectedPlates = values['-SELECT-']
            print(selectedPlates)
            for plate in selectedPlates:
                 window.hide() #or close?
                 displayEditPlateQuestion(plate)
            break
        elif event == "No":
            break
    values = None
    window.close()

def errorPlateEdit():
    layout = [
        [gui.Push(), gui.Text("Nesprejemljiva sprememba"), gui.Push()],
        [gui.Push(), gui.Text("V bazo se bo shranila originalna"), gui.Push()]
    ]

    window = gui.Window("Oh no", layout)

    while True:
        event, values = window.Read()

        if event == gui.WINDOW_CLOSED:
            break
    window.close()

def successSave():
    layout = [
        [gui.Push(), gui.Text("Uspešno shranjeno v bazo podatkov"), gui.Push()]
    ]

    window = gui.Window("Yay", layout)

    while True:
        event, values = window.Read()

        if event == gui.WINDOW_CLOSED:
            break
    window.close()

def unsuccessSave():
    layout = [
        [gui.Push(), gui.Text("Shranjevanje ni bilo uspešno :("), gui.Push()]
    ]

    window = gui.Window("Oh no", layout)

    while True:
        event, values = window.Read()

        if event == gui.WINDOW_CLOSED:
            break
    window.close()
