import sys
from os import listdir, rename
from os.path import isfile, join, splitext
from PIL import Image
import colors
from datetime import datetime

photosPath = "./example-photos"
files = [f for f in listdir(photosPath) if isfile(join(photosPath, f))]

decision = input(f'{colors.bcolors.WARNING}{len(files)} arquivos encontrados para processar, deseja continuar? (Y/n) {colors.bcolors.ENDC}') or 'Y'

if decision.upper() != 'Y':
    print(f'{colors.bcolors.DANGER}Adeus...')
    sys.exit()

for fileName in files:
    filePath = f'{photosPath}/{fileName}'
    fileExtension = splitext(filePath)[1]
    file = Image.open(f'{filePath}')
    exif = file.getexif()
    file.close()

    if not exif:
        print(f'{colors.bcolors.DANGER}ERRO: O arquivo {fileName} não contém o metadado. {colors.bcolors.ENDC}')

    dateTaken = exif[306]
    formattedDateTaken = datetime.strptime(dateTaken, '%Y:%m:%d %H:%M:%S')
    formattedDateTaken = formattedDateTaken.strftime('%d-%m-%Y %H:%M:%S')

    newFileName = f'a{fileExtension}'
    newFilePath = f'{photosPath}/{newFileName}'

    rename(f'{filePath}', f'{newFilePath}')
    print(f'{colors.bcolors.SUCCESS}Processado: {fileName} -> {newFileName} {colors.bcolors.ENDC}')
