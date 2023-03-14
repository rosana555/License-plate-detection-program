import cv2 as cv
import pytesseract as tes
import re


def live():
    readLicensePlates = []
    liveCam = cv.VideoCapture(0)

    while True:
        ret, frame = liveCam.read()

        frame, number = detect(frame)
        for num in number:
            if addPlate(readLicensePlates, num):
                readLicensePlates.append(num)
            else:
                num = ""

        cv.imshow('Live video', frame)

        if cv.waitKey(1) == ord('q'):
            break

    liveCam.release()
    cv.destroyAllWindows()
    return readLicensePlates

def readFromPhoto(imgPath):

    img = cv.imread(imgPath)

    if img is None:
        print("Unable to open photo")
        return None

    img, number = detect(img)
    cv.imshow("Detected plate", img)

    cv.waitKey(0)
    cv.destroyAllWindows()
    return number

def detectFromVideo(videoURL):
    readLicensePlates = []


    video = cv.VideoCapture(videoURL)

    if not video.isOpened():
        print("Unable to open video")
        return

    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break
        frame = cv.resize(frame, (800, 600))

        frameDetected, number = detectPlates(frame)

        for num in number:
            if addPlate(readLicensePlates, num):
                readLicensePlates.append(num)
            else:
                num = ""
        cv.imshow("video", frameDetected)

        if cv.waitKey(15) == ord('q'):
            break

    video.release()
    cv.destroyAllWindows()
    return readLicensePlates



def detect(img):
    img, number = detectPlates(img)
    return img, number

def detectPlates(img):
    imgPrepared = prepareImageForDetection(img)

    cascade_file = cv.CascadeClassifier("licensePlates.xml")

    detectedPlates = cascade_file.detectMultiScale(imgPrepared, minNeighbors=5, scaleFactor=1.01, minSize=(45, 100), maxSize=(350, 200))

    textRecognized = []
    for x, y, width, height in detectedPlates:
        croppped_img = imgPrepared[y + 10:y + height - 15, x + 5:x + width - 20] #play around w the values
        cv.imshow("cropped", croppped_img)
        text = readPlate(croppped_img)
        text = validatePlate(text)
        textRecognized.append(text)
        cv.rectangle(img, pt1=(x + 10, y + 15), pt2=(x + width - 10, y + height - 10), color=(30, 180, 45), thickness=2)
        cv.putText(img, text=str(text), org=(x + int(width / 5), y), fontFace=cv.FONT_HERSHEY_COMPLEX, fontScale=1,
                   color=(0, 0, 0), thickness=2)
    return img, textRecognized


def validatePlate(plate):

    places = ['MB', 'LJ', 'CE', 'KK', 'KR', 'NG', 'GO', 'PO', 'KP', 'SG', 'MS', 'NM']

    if len(plate) >= 7:
        for kr in places:
            if kr in plate:
                index = plate.find(kr)
                return plate[index:index+7]
    elif len(plate) >= 5:
        return plate
    else:
        return ""

def readPlate(croppedImg):
    img = prepareImageForReading(croppedImg)
    pattern = r"[^A-Z0-9]"


    text = tes.image_to_string(img, config='--psm 7') #3, 4, 9
    cleaned_text = re.sub(pattern, '', text)
    return cleaned_text


def addPlate(readPlatesArray, number):

    if (number is None) or (number == ''):
        return False
    elif number in readPlatesArray:
        return False
    elif len(number) < 4:
        return False
    else:
        return True


"""
PREPARATION
"""

def prepareImageForDetection(img):
    img = cv.GaussianBlur(img, (5, 7), 1)

    return img


def prepareImageForReading(img):
    # img2 = cv.resize(src=img, dsize=(555, 200), interpolation=cv.INTER_NEAREST)
    img2 = cv.resize(img, None, fx=2, fy=2)
    grey = cv.cvtColor(img2, cv.COLOR_BGR2GRAY)
    noise = cv.medianBlur(grey, 7)  # choose a 6 or 7
    thresh = cv.threshold(noise, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)[1]
    invert = 255 - thresh
    return invert