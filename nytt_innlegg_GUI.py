# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image, ExifTags
from os import listdir
import os
from datetime import datetime
import codecs
from ftplib import FTP
import webbrowser

#GLOBAL VARIABLES
imgfiles = []
texts = []
imagesToUpload = []

files = listdir('innlegg')
files.sort(key=len)
newFileNumber = len(files) + 1

def open_index_file():
    filename = 'index.html'
    url = 'file://' + os.path.realpath(filename)
    webbrowser.open(url)

def upload():
    # Connect to server and log in
    ftp = FTP('*') #**** = ftp.'domain'
    ftp.login(user ='*',passwd ='**') # * = username, ** = password
    # laste opp index.html
    ftp.cwd('/www/')   #plassering
    filename = 'index.html'
    ftp.storbinary('STOR ' + filename, open(filename, 'rb'))

    # laste opp bilder
    imagefiles = listdir('bilder')  #liste med
    ftp.cwd('bilder/')
    for image in imagesToUpload:
        imgfile = 'bilder/' + image
        ftp.storbinary('STOR ' + image, open(imgfile, 'rb'))

        # QUIT
    ftp.quit()

def rotate_image(image):
    for orientation in ExifTags.TAGS.keys():
        if ExifTags.TAGS[orientation] =='Orientation':
            break
    exif = dict(image._getexif().items())
    if exif[orientation] == 3:
        image= image.rotate(180, expand=True)
    elif exif[orientation] == 6:
        image = image.rotate(270, expand = True)
    elif exif[orientation] == 9:
        image = image.rotate(90, expand = True)
    return image

def save_pictures(fileNr):  #rotere å lagre alle nye bilder i mappen bilder
    for i in range(len(imgfiles)):
        image = Image.open(imgfiles[i])
        image = rotate_image(image)
        newImagePath = 'bilder/' + str(fileNr) + '_' + str(i+1) +'.jpg'
        image.save(newImagePath)
        image.close()
        imagesToUpload.append(str(fileNr)+ '_' + str(i+1)+'.jpg')

def make_date_line():
    date_and_time = datetime.now().strftime('%d.%m.%Y    %H:%M')
    return '&' + date_and_time + '\n'

def make_content(fileNr):
    content = title_entry.get() +'\n'
    content += make_date_line()
    content += main_text.get(1.0, END)
    for i in range(len(imgfiles)):
        #legg til bilde
        imageName = str(fileNr) + '_' + str(i+1)
        content += '#' +imageName + '\n'

        content += texts[i].get(1.0,END)

    return content

def savePost(fileNr, content):
    filePath = 'innlegg/' + str(fileNr) +'.txt'
    f = open(filePath, 'w+') #w+ -> write, + create file if it doesn't exist
    f.write(content)
    f.close()

def add_image_code(imgLine):
    imgNr = imgLine[1:].strip('\n')
    print('imgNr', imgNr)

    imgFilename = "bilder/" + imgNr + ".jpg"
    print(imgFilename)

    #sjekker om bildet eksisterer i mappen
    exist = os.path.isfile(imgFilename)
    assert(exist), "Kan ikke finne bilde " + imgNr + " under mappen bilder. Sjekk om den ligger der eller spørr om help."

    #roterer bilde om det er feil vei
    #SE MER PÅ DETTE, DET ØDELEGGER EXIFDATAEN
    try:
        rotate_image(imgFilename)
    except:
        pass

    #returner riktig kodesnutt
    print(imgLine,imgNr)
    return '<img src=' + imgFilename + ' class="img-fluid"> <br>'

def makeHtmlScript(files):
    script=''
    for i in range(len(files) -1,-1,-1):

        f=open("innlegg/" + files[i], "r",)
        content=f.readlines()
        f.close()

        #den første linjen blir lagt til variabelen "heading" og resten av linjene blir lagt til i variabelen "tekst"
        heading = '<h3>' + content[0] + '</h3>'

        #den andre linjen er dato
        date = '<h4> Publisert: '+ content[1].strip('&') + '</h4>'

        #teksten i innlegget
        text = ''
        for line in content[2:]:
            if line[0] ==  "#":
                text += add_image_code(line)
            else:
                text+= line +'<br>'  # legger til '<br>' slik at man får linjeskift på hjemmesiden


        script += heading + date + text + '<br> <br>'

    return script

def write_to_htmlfile(content):
    f=codecs.open("mal.html", 'r',"utf-8")
    lines = f.readlines()
    f.close()

    f=codecs.open("index.html","w","utf-8")
    for line in lines:
        if line.startswith("&&&"):
            f.write(content)
        else:
            f.write(line)
    f.close()

def save():

    content = make_content(newFileNumber)
    #testLabel = Label(root, text= allText)   #test
    #testLabel.pack(side= TOP)               #test

    savePost(newFileNumber, content)
    save_pictures(newFileNumber)

    files = listdir('innlegg')
    files.sort(key=len)
    content_html = makeHtmlScript(files)
    testLabel = Label(root, text = content_html)
    testLabel.pack()
    write_to_htmlfile(content_html)



def add_picture():
    #let user choose image
    filename = filedialog.askopenfilename()   #add restriction on filetype
    imgfiles.append(filename)

    img = Image.open(filename)
    img = img.resize((150,150),Image.ANTIALIAS)  # juster resize?

    img = ImageTk.PhotoImage(img)
    panel = Label(frame, image=img)
    panel.image = img
    panel.pack()
def add_textbox():
    newText = Text(frame, height=10)
    texts.append(newText)
    newText.pack()
def add_picture_cb():
    add_picture()
    add_textbox()
    canvas.create_window(0, 0, anchor='nw', window=frame)
    canvas.update_idletasks()

    canvas.configure(scrollregion=canvas.bbox('all'), yscrollcommand=scrollbar.set)
    canvas.pack(fill='both', expand=True, side='left')

root = Tk()

canvas = Canvas(root, height =700, width =700)

scrollbar = Scrollbar(root,orient='vertical' ,command=canvas.yview)   # er orient unødvendig?
scrollbar.pack(side= RIGHT, fill=Y)

frame= Frame(canvas)

canvas.configure(yscrollcommand = scrollbar.set)
canvas.create_window(0,0, window=frame, anchor = 'nw')

save_button = Button(frame,text='LAGRE', command= save)
save_button.pack()

preview_button = Button(frame, text='Forhåndsvis index.html', command= open_index_file)
preview_button.pack()


upload_button = Button(frame, text='LAST OPP', command= upload)
upload_button.pack()

add_picture_button = Button(frame, text='Legg til bilde', command= add_picture_cb )
add_picture_button.pack()

title_label = Label(frame, text='Overskrift')
title_label.pack()
title_entry = Entry(frame)
title_entry.pack()


main_text_label = Label(frame, text='Tekst:')
main_text_label.pack()
main_text = Text(frame, height=10)
main_text.pack()

canvas.create_window(0,0,anchor='nw', window=frame)
canvas.update_idletasks()

canvas.configure(scrollregion=canvas.bbox('all'),yscrollcommand= scrollbar.set)
canvas.pack(fill='both',expand=True, side ='left')
scrollbar.pack(fill='y', side= 'right')

root.mainloop()