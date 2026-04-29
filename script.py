import cv2
import numpy as np
import pytesseract
import easyocr
import argparse

parser = argparse.ArgumentParser(prog='BF-Tabscan', description='Uses OCR to read a Blockfront tablist and return a table')

parser.add_argument('image')
parser.add_argument("-gpu","--use_gpu",help="Enable GPU scanning",nargs='?', const=True, default=False)
parser.add_argument("-load-tesseract",'--load_pytesseract',help="Calls tesseract ",nargs='?', const=True, default=False)
args = parser.parse_args()

img = cv2.imread(args.image)
#note: Tesseract OCR uses OEM 2, requiring additional ENG training data to be downloaded from their repository.
if load_pytesseract = True:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

class interest_region:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

listing_ht = 30

team1_starting_y = 204
interentry_buffer = 3
team_mirror_distance = 615

usr_x = 820
usr_wd = 385

cls_x = 1205
cls_wd = 120

ks_x = 1470
ks_wd = 45

as_x = 1560
as_wd = 45

cp_x = 1650
cp_wd = 45

sc_x = 1730
sc_wd = 60

spacing = interentry_buffer + listing_ht

relativerankcolorchecky = 5
relativerankcolorcheckx = 1

# Lists used to store the raw OCR results for each category.
userlist = []
classeslist = []
killslist = []
aslist = []
cplist = []
sclist = []

# Function that performs cleanup/error correction for the classes list. The single word entries are often misread by the OCR, but have expected values that can be corrected for (unlike usernames).
def CleanupClasses():
    global classeslist
    cycle = 0
    for listing in classeslist:
        charcorrected = ""
        for char in str(listing):
            if char == "1":
                char = "I"
            elif char == "¥":
                char = ""
            charcorrected += char

        if "niper" in str(charcorrected).strip().lower():
            charcorrected = str(charcorrected).strip().split("r", 1)[1]
            charcorrected = "Sniper" + charcorrected
        elif "medic" in str(charcorrected).strip().lower():
            charcorrected = str(charcorrected).strip().split("c", 1)[1]
            charcorrected = "Medic" + charcorrected
        elif "eman" in str(charcorrected).strip().lower():
            charcorrected = str(charcorrected).strip().split("n", 1)[1]
            charcorrected = "Rifleman" + charcorrected
        elif "lt." in str(charcorrected).strip().lower():
            charcorrected = str(charcorrected).strip().split("e", 1)[1]
            charcorrected = "Lt. Rifle" + charcorrected
        elif "tank" in str(charcorrected).strip().lower():
            charcorrected = str(charcorrected).strip().split("k", 1)[1]
            charcorrected = "Anti-tank" + charcorrected
        elif "unner" in str(charcorrected).strip().lower():
            charcorrected = str(charcorrected).strip().split("r", 1)[1]
            charcorrected = "Gunner" + charcorrected
        elif "upport" in str(charcorrected).strip().lower():
            charcorrected = str(charcorrected).strip().split("t", 1)[1]
            charcorrected = "Support" + charcorrected

        classeslist[cycle] = charcorrected
        cycle += 1

values = [   
                interest_region(usr_x, team1_starting_y, usr_wd, listing_ht),
                interest_region(usr_x, team1_starting_y + spacing, usr_wd, listing_ht),
                interest_region(usr_x, team1_starting_y + 2 * spacing, usr_wd, listing_ht),
                interest_region(usr_x, team1_starting_y + 3 * spacing, usr_wd, listing_ht),
                interest_region(usr_x, team1_starting_y + 4 * spacing, usr_wd, listing_ht),
                interest_region(usr_x, team1_starting_y + 5 * spacing, usr_wd, listing_ht),
                interest_region(usr_x, team1_starting_y + 6 * spacing, usr_wd, listing_ht),
                interest_region(usr_x, team1_starting_y + 7 * spacing, usr_wd, listing_ht)
                ]

uppercolorlimit = np.array([40, 70, 70])
lowercolorlimit = np.array([30, 60, 60])

reader = easyocr.Reader(['en'], gpu=args.use_gpu)

teamtarget = np.array([70, 125, 121])
teamlower = teamtarget - 10
teamupper = teamtarget + 10

whitetarget = np.array([240, 240, 240])
lowerwhite = whitetarget - 15
upperwhite = whitetarget + 15
yellowtarget = np.array([82, 247, 247])
loweryellow = yellowtarget - 10
upperyellow = yellowtarget + 10

def scancolumn(targetlist=list):
    for region in values:
        pixel = img[region.y + relativerankcolorchecky, usr_x - relativerankcolorcheckx]
        if np.all((pixel >= lowercolorlimit) & (pixel <= uppercolorlimit)):
            roi = img[region.y-interentry_buffer:region.y+region.height+interentry_buffer, region.x:region.x+region.width]

            mask = np.all(((roi >= teamlower) & (roi <= teamupper)) | ((roi >= lowerwhite) & (roi <= upperwhite)), axis=-1)
            roi[mask] = [244, 244, 244]
            roi[~mask] = [0, 0, 0]

            rescaled_roi = cv2.resize(roi, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST_EXACT)
            if targetlist == userlist or classeslist:
                results = reader.readtext(rescaled_roi, detail=0, paragraph=False, allowlist=' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_[]')
            else:
                results = reader.readtext(rescaled_roi, detail=0, paragraph=False, allowlist=' 0123456789')

            try:
                text = results[0]
            except IndexError:
                text = "ERROR!"

            targetlist.append(str(text).strip())
            
scancolumn(userlist)

# I have this one as a separate function because it scans for yellow text instead of green, and uses pytesseract instead of easyocr.
for region in values:
    region.width = cls_wd
    region.x = cls_x

    pixel = img[region.y + relativerankcolorchecky, usr_x - relativerankcolorcheckx]
    if np.all((pixel >= lowercolorlimit) & (pixel <= uppercolorlimit)):
        roi = img[region.y-interentry_buffer:region.y+region.height+interentry_buffer, region.x:region.x+region.width]

        mask = np.all(((roi >= loweryellow) & (roi <= upperyellow)) | ((roi >= lowerwhite) & (roi <= upperwhite)), axis=-1)
        roi[mask] = [244, 244, 244]
        roi[~mask] = [0, 0, 0]

        rescaled_roi = cv2.resize(roi, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST_EXACT)

        text = pytesseract.image_to_string(rescaled_roi, config='--oem 2 --psm 7')

        classeslist.append(str(text).strip())

for region in values:
    region.width = ks_wd
    region.x = ks_x

scancolumn(killslist)

for region in values: 
    region.width = as_wd
    region.x = as_x

scancolumn(aslist)

for region in values:
    region.width = cp_wd
    region.x = cp_x

scancolumn(cplist)

for region in values:
    region.width = sc_wd
    region.x = sc_x

scancolumn(sclist)

CleanupClasses()

#prints out all the values in a neat table format into the console.
print("```")
print("Allied Team")
print("|    USERNAME (UNEDITED)    |      CLASS      | KILLS | ASSISTS | CAPTURES | SCORE |")
print("------------------------------------------------------------------------------------")
for i in range(len(userlist)):
    print(f"| {userlist[i]:<25} | {classeslist[i]:<15} | {killslist[i]:<5} | {aslist[i]:<7} | {cplist[i]:<8} | {sclist[i]:<5} |")


userlist.clear()
classeslist.clear()
killslist.clear()
aslist.clear()
cplist.clear()
sclist.clear()

#readjusts the color limits to be the red axis color instead of the green allies color
uppercolorlimit = np.array([30, 35, 75])
lowercolorlimit = np.array([20, 25, 60])

teamtarget = np.array([48, 55, 125])
teamlower = teamtarget - 10
teamupper = teamtarget + 10

for region in values:
    region.y = region.y + team_mirror_distance
    region.width = usr_wd
    region.x = usr_x

scancolumn(userlist)

for region in values:
    region.width = cls_wd
    region.x = cls_x

    pixel = img[region.y + relativerankcolorchecky, usr_x - relativerankcolorcheckx]
    if np.all((pixel >= lowercolorlimit) & (pixel <= uppercolorlimit)):
        roi = img[region.y-interentry_buffer:region.y+region.height+interentry_buffer, region.x:region.x+region.width]

        mask = np.all(((roi >= loweryellow) & (roi <= upperyellow)) | ((roi >= lowerwhite) & (roi <= upperwhite)), axis=-1)
        roi[mask] = [244, 244, 244]
        roi[~mask] = [0, 0, 0]

        rescaled_roi = cv2.resize(roi, None, fx=4, fy=4, interpolation=cv2.INTER_NEAREST_EXACT)

        text = pytesseract.image_to_string(rescaled_roi, config='--oem 2 --psm 7')

        classeslist.append(str(text).strip())

for region in values:
    region.width = ks_wd
    region.x = ks_x

scancolumn(killslist)

for region in values:
    region.width = as_wd
    region.x = as_x

scancolumn(aslist)

for region in values:
    region.width = cp_wd
    region.x = cp_x

scancolumn(cplist)

for region in values:
    region.width = sc_wd
    region.x = sc_x

scancolumn(sclist)
CleanupClasses()

print("Axis Team")
print("|    USERNAME (UNEDITED)    |      CLASS      | KILLS | ASSISTS | CAPTURES | SCORE |")
print("------------------------------------------------------------------------------------")
for i in range(len(userlist)):
    print(f"| {userlist[i]:<25} | {classeslist[i]:<15} | {killslist[i]:<5} | {aslist[i]:<7} | {cplist[i]:<8} | {sclist[i]:<5} |")
print("```")
