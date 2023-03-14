import mysql.connector
import datetime

cnx = mysql.connector.connect(user="root", password="temptemp", host="localhost", database ="licensePlatedb")


def checkInDB(plate):
    cursor = cnx.cursor()
    query = "SELECT * FROM registrskeTablice WHERE stevilka = %s"

    print(plate)
    cursor.execute(query, (plate,))
    result = cursor.fetchall()
    if cursor.rowcount > 0:
        return True
    else:
        return False


def saveToDB(plate, editPlate):
    print(f"DATE: {datetime.datetime.now()}")
    cursor = cnx.cursor()

    places = ['MB', 'LJ', 'CE', 'KK', 'KR', 'NG', 'GO', 'PO', 'KP', 'SG', 'MS', 'NM']

    place = None
    for kr in places:
        if kr in plate:
            place = kr


    #so table could have an original/read plate and also edited plate

    querry = "INSERT INTO registrskeTablice (stevilka, stevilkaOriginal, obcina, casShranjevanja) VALUES (%s, %s, %s, %s)"

    time = datetime.datetime.now()

    cursor.execute(querry, (editPlate, plate, place, time.strftime('%Y-%m-%d %H:%M:%S')))

    cnx.commit()

    if(checkInDB(editPlate)):
        return True
    else:
        return False


def validateEditedPlate(edit, original):
    if abs(len(original) - len(edit)) > 3:
        return False

    diffCount = 0
    i, j = 0, 0
    while i < len(original) and j < len(edit):
        if original[i] != edit[j]:
            diffCount += 1
            if diffCount > 3:
                return False

            if len(original) > len(edit):
                i += 1
            elif len(edit) > len(original):
                j += 1

        i += 1
        j += 1
    print(diffCount <= 3)
    return diffCount <= 3


