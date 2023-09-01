import sys
from os import listdir, rename
from os.path import isfile, join, splitext
from PIL import Image
import colors
from datetime import datetime
from progress.bar import ChargingBar
from time import sleep
from tkinter import Tk
from tkinter.filedialog import askdirectory

root = Tk()
print("Aguardando seleção...")
photosPath = askdirectory(title='Selecione a pasta onde estão as fotos')
root.destroy()

if photosPath == "":
    print("Nenhuma pasta foi selecionada.")
    exit()

print(f"{colors.bcolors.WARNING}Pasta selecionada: {photosPath}{colors.bcolors.ENDC}")

files = [
    f for f in listdir(photosPath)
    if isfile(join(photosPath, f))
    and f.upper().endswith((".JPG", ".JPEG", ".PNG", ".GIF", ".MOV", ".MP4", ".AVI", ".JFIF", ".WEBP"))
]
totalFiles = len(files)

if totalFiles == 0:
    print(f"{colors.bcolors.DANGER}Não há arquivos na pasta selecionada.{colors.bcolors.ENDC}")
    exit()

decision = input(
    f'{colors.bcolors.SUCCESS}{totalFiles} arquivos encontrados para processar, deseja continuar? (y/N) {colors.bcolors.ENDC}') or 'N'

if decision.upper() != 'Y':
    print(f'{colors.bcolors.DANGER}Adeus...{colors.bcolors.ENDC}')
    sys.exit()

bar = ChargingBar(f'Processando ', max=totalFiles)
bar.color = "blue"

filesRenamed = 0
for fileName in files:
    bar.bar_prefix = f'{fileName}  '
    bar.suffix = f'%(percent)d%% {bar.elapsed}s'

    filePath = f'{photosPath}/{fileName}'
    fileExtension = splitext(filePath)[1]
    file = Image.open(f'{filePath}')
    exif = file.getexif()
    file.close()

    if not exif:
        print(f'{colors.bcolors.DANGER}ERRO: O arquivo {fileName} não contém o metadado. {colors.bcolors.ENDC}')
        bar.next()
        break

    dateTaken = exif[306]
    formattedDateTaken = datetime.strptime(dateTaken, '%Y:%m:%d %H:%M:%S')
    formattedDateTaken = formattedDateTaken.strftime('%d-%m-%Y %H-%M-%S')

    newFileName = f'{formattedDateTaken}{fileExtension}'
    newFilePath = f'{photosPath}/{newFileName}'

    repeatedFileCounter = 0
    while isfile(newFilePath) == 1:
        repeatedFileCounter += 1
        newFileName = f'{formattedDateTaken}-{repeatedFileCounter}{fileExtension}'
        newFilePath = f'{photosPath}/{newFileName}'

    rename(f'{filePath}', f'{newFilePath}')
    filesRenamed += 1
    sleep(0.1)
    bar.next()

bar.finish()
print(f"{colors.bcolors.SUCCESS}{filesRenamed} arquivos renomeados em {bar.elapsed} segundos.{colors.bcolors.ENDC}")
