import os
import re
import json
import codecs
from collections import defaultdict
import string

library_path="D://MyJsonData"
data_path="C://Users//George//Desktop//AllData"
test_path="C://Users//George//Desktop//test"
error_log="C://Users//George//Desktop//error_log"

libraryISBN = {}
libraryTITLE = {}
conflicts = defaultdict(list)

_counter_ = 0


def getCode(elt):
    # print("code is " + elt.split(' ')[0])
    return elt.split(' ')[0]


def getValue(elt):
    return ' '.join(elt.split(' ')[4:])


def getTitle(elt):
    title = ' '.join(elt.split()[2:]).rstrip(' .,;\'\"[]:').split('/$$c')
    return title

def getTitle(elt):
    title = ' '.join(elt.split()[2:]).rstrip(' .,;\'\"[]:')
    #print title
    return title



def isbnOfBookInLib(title, lib):
    books = lib.values()
    for book in books:
        if book['title'] == title:
            return(book['isbn'])

def compareFeatures(f1, f2):
    # relaxed features, case , no nikud pisuk
    #print f1
    f1=''.join([letter.lower() for letter in f1 if letter.isalnum() or letter == ' '])
    #print f1
    f2=''.join([letter.lower() for letter in f2 if letter.isalnum() or letter == ' '])
    #print f2
    return (f1 == f2)


def addBookToLibOld(bookInst,allBooks): ##old function
    # isbn should be an identifier to a book, but not always present. make id either title or isbn
    #in order to add a book to library, make it isbn-num:and book entry

    bookISBN = bookInst['isbn']
    bookTitle= bookInst['title']

    if bookISBN:
        if bookISBN in allBooks.keys():
            #print(allBooks[bookISBN])
            allBooks[bookISBN]=mergeBooks(allBooks[bookISBN],bookInst)
        elif bookTitle in allBooks.keys(): #book was previously archived with title
            allBooks[bookISBN]=mergeBooks(allBooks[bookTitle],bookInst)
            del allBooks[bookTitle]
        else:
            allBooks[bookISBN]=bookInst

    elif bookTitle:
        isbn=isbnOfBookInLib(bookTitle,allBooks)

        if bookTitle in allBooks.keys():
            allBooks[bookTitle]=mergeBooks(allBooks[bookTitle],bookInst)
        elif isbn: #if it has isbn
            allBooks[isbn]=mergeBooks(allBooks[isbn],bookInst)
        else:
            allBooks[bookTitle]=bookInst

    return(allBooks)


def mergeBooks(book1,book2):

    for feature,value in book1.items():
        if type(value) is list:
            if feature is 'subjects':
                book1[feature].extend(book2[feature])
            else:
                if value and book2[feature]:
                    book1[feature]=list(set(value).union(set(book2[feature])))
                else:
                    book1[feature].extend(book2[feature])

        #elif value != book2[feature]:
        elif not compareFeatures(value, book2[feature]):
            if not value:
                book1[feature] = book2[feature]
            elif not book2[feature]:
                continue
            else:
                book1['conflicts'].append([feature, value, book2[feature]])
                conflicts[(book1['title'], book1['isbn'])].append([feature, value, book2[feature]])

    return(book1)


def makebook():
    return ({"isbn":"",
             "title":"",
             "fulltitle":"",
             "volume":[],
             "volName":"",
             "subtitle":[],
             "format":"",
             "serialNum":[],
             "editors":[],
             "subjects":[],
             "authors":[],
             "titleAdditions":[],
             "authorDates":[],
             "language":"",
             "sourceLanguage":"",
             "publisher":[],
             "publisherAddress":[],
             "date":[],
             #"physical":[],
             "pages":[],
             "addendum":[],
             "size":[],
             "comments":[],
             "dewey":"",
             "trans_eds_ills":[],
             "conflicts":[]})



def bookInstance(book):
    bookInst= makebook()
    for elt in book:
        code = getCode(elt)
        #print(code)
        if code == 'FMT':
            bookInst['format']= getValue(elt) #book or video?
        elif code == '001':
            bookInst['serialNum'].append(getValue(elt))
        elif code == '084': #dewey
            bookInst['dewey']=getValue(elt)[3:]
        elif code == '1001':
            authorInfo=' '.join(elt.split(' ')[3:]).split('$$d')
            #print(authorInfo[0])
            bookInst['authors'].append(authorInfo[0][3:].rstrip(' ,.;-/:'))
            if len(authorInfo)>1:
                bookInst['authorDates'].append(authorInfo[1].rstrip(' ,.;-/:'))
        elif code.startswith('245'):  # 24501 or code == '24500':
            title = getTitle(elt).split('$$')[1:]

            #mainTitle=title[0].split('$$')
            #print(mainTitle[0].split('$$h')[0][3:])
            #print title[0]
            for elt in title:
                beginner=elt[0]
                #print beginner
                if beginner == 'a':
                    bookInst['fulltitle']=elt[1:].rstrip(' \t.,;/:')
                    #print elt[1:].rstrip(' \t.,;/:')

                    bookInst['title']=elt[1:].rstrip(' \t.,;/:').replace("<","").replace(">","")
                elif beginner == 'b':
                    bookInst['subtitle'].append(elt[1:].rstrip(' \t.,;/:'))
                elif beginner == 'n':
                    bookInst['volume']=elt[1:].rstrip(' \t.,;/:')
                elif beginner == 'p':
                    bookInst['volName']= elt[1:].rstrip(' \t.,;/:')
                elif beginner == 'c':
                    bookInst['titleAdditions'].append(elt[1:])



                    #if len(title)>1:
                    #    bookInst['titleAdditions'].extend(title[1:])

                    #if len(mainTitle)>1:
                    #    bookInst['subtitle']=mainTitle[1:]

        elif code.startswith("6"):#code == '650' or 651 or code=='695' or code=='6000' or '60014'':
            subject = ' '.join(elt.split(' ')[3:]).rstrip('.,/;:[]').split('$$')[1:]
            processed_subject = ""

            for s in subject:
                #print subject
                first = s[0]
                rest = s[1:]

                if first == 'a':
                    processed_subject = rest
                elif first == 'x': #sub
                    processed_subject = processed_subject + " **sub: " + rest
                elif first == 'y':
                    processed_subject = processed_subject + " **period: " + rest
                elif first == 'd':
                    processed_subject = processed_subject + " **date: " + rest
                elif first == 'z':
                    processed_subject = processed_subject + " **location: " + rest
                elif first == ('b' or 'c'):
                    processed_subject += " " + rest
                else:
                    processed_subject = processed_subject + " **" + first + ": " + rest


            bookInst['subjects'].append(processed_subject)

        elif code == '020':
            bookInst['isbn']=getValue(elt).split(' ')[0][3:].split("$$")[0] #some foreign language books has $#c
        elif code.startswith('041'):
            language = getValue(elt)[3:].split('$$')
            #print language[0]
            if len(language) > 1:
                bookInst['sourceLanguage'] = language[1][1:]
            bookInst['language'] = language[0]
        elif code == "260":
            publisher = getValue(elt).rstrip(' ,.;-/:[]').rsplit('$$')[1:]
            #print publisher[0][1:]
            bookInst['publisherAddress'].extend([address[1:].rstrip(",][/ .:") for address in publisher if address.startswith('a')])
            bookInst['publisher'].extend([pub[1:].rstrip(",][ .:") for pub in publisher if pub.startswith('b')])
            bookInst['date'].extend([date[1:].rstrip(", ][.:") for date in publisher if date.startswith('c')])
        elif code == "300":
            physical = getValue(elt).rstrip(' ,.;-/:[]').rsplit('$$')[1:]
            bookInst['pages'].extend([address[1:].rstrip(",][/ .:;") for address in physical if address.startswith('a')])
            bookInst['addendum'].extend([pub[1:].rstrip(",][ ;.:") for pub in physical if pub.startswith('b')])
            bookInst['size'].extend([date[1:].rstrip(", ][.:;") for date in physical if date.startswith('c')])
        elif code.startswith("5"):
            bookInst['comments'].append(getValue(elt).rstrip(' ,.;-/:[]'))
        elif code.startswith("700"):
            bookInst['trans_eds_ills'].append(' '.join(elt.split(' ')[3:]).rstrip('.,/;:[]'))
    #print(book)
    return(bookInst)

def makeDirForLetter(letter):
    dir = os.path.join(library_path,letter + "_dir")
    if not os.path.exists(dir):
        print "Creating new directory \"%s\"" % dir
        os.makedirs(dir)
    return(dir)

def first_letter(name):
    return name[0]

def writeBook(bookInst, uniqueID):

    uniqueID = re.sub(r'[\'"~`!@#$%^&*()=+_\[\]{}:;/.,\\|}<>-]', '', uniqueID)
    letter = first_letter(uniqueID.strip())

    try:
        dir=makeDirForLetter(letter)
    except:
        print uniqueID
        print letter
        exit(1)

    #print uniqueID
    uniqueID = uniqueID.replace('/', "")
    uniqueID = uniqueID+".json" #creating the files as json
    #print uniqueID
    try:
        with codecs.open(os.path.join(dir, uniqueID), 'w', encoding='utf-8') as f:
            print "Writing to file \"%s\"" % os.path.join(dir, uniqueID)
            f.write(json.dumps(bookInst, indent=4, ensure_ascii=False, encoding="utf-8"))
    except:
        with codecs.open(error_log, 'a', encoding='utf-8') as e:
            e.write("Book " + bookInst['title'] + " uniqueID " + uniqueID + "\n")


def readBook(uniqueID):
    dir = os.path.join(library_path, first_letter(uniqueID)+"_dir")
    book=makebook()
    try:
        with codecs.open(os.path.join(dir, uniqueID), 'r', encoding='utf-8') as f:
            book=json.load(f)
    except:
        with codecs.open(error_log, 'a', encoding='utf-8') as e:
            e.write("Book  uniqueID " + uniqueID + "\n")
    return(book)


def addBookToLib(bookInst): #book is a dictionary
    #pprint.pprint(bookInst)
    bookISBN = bookInst['isbn']
    bookTitle= bookInst['title']

    #see if this book was archived, if so merge
    libBook={}
    #there is isbn, and it already in lib
    if bookISBN:
        if bookISBN in libraryISBN.keys():
            libBook = readBook(bookISBN)

    # if no isbn given, check if book in lib
    elif bookTitle:
        if bookTitle in libraryTITLE.keys():
            libBook = readBook(bookTitle)

    if libBook:
        libBook = mergeBooks(libBook, bookInst)
        #update the list of ISBN
        bookISBN=libBook['isbn']
    else:
        libBook = bookInst


    if bookISBN:
        libraryISBN[bookISBN] = bookTitle
        writeBook(libBook, bookISBN)
    if bookTitle:
        libraryTITLE[bookTitle] = bookISBN
        writeBook(libBook, bookTitle)



newRecord=True
thisBook=[]
currentBook = dict()
#currentBook['FMT']='BK'
allBooks = {}

#
#with codecs.open(os.path.join(test_path, "sample.marc"), 'rb', encoding="utf-8") as fh:
with codecs.open(os.path.join(data_path, "doc.seqaa"), 'rb',encoding="utf-8") as fh:

    #reader = MARCReader(fh)

    for line in fh: #must make a record from each field
        lineElts =line.split(' ')
        #print lineElts[3]
        if newRecord:
            bookSerial = lineElts[0]
            #print(bookSerial)
            thisBook.append(line[10:].rstrip('\n'))
            newRecord=False

        elif bookSerial == lineElts[0]: #not a new book
            thisBook.append(line[10:].rstrip('\n'))

        elif bookSerial is not lineElts[0]: #new book
            #_counter_ +=1
            #if _counter_ % 1000 is 0:
            #    print ".",
            #elif _counter_ % 100000 is 0:
            #    print "\n"

            bookSerial = lineElts[0]
            newRecord=True
            addBookToLib(bookInstance(thisBook))
            thisBook=[line[10:].rstrip('\n')]
            #print '.',


#data=json.dumps(allBooks, indent=4, ensure_ascii=False)
#print "writing to file now"


isbnFile = 'C://Users//George//Desktop//library//booksISBN.json'
titlesFile = 'C://Users//George//Desktop//library//booksTITLES.json'
conflictsFile = 'C://Users//George//Desktop//library//conflicts.json'

with codecs.open(isbnFile, 'w', encoding='utf-8') as f:
    f.write(json.dumps(libraryISBN, indent=4, ensure_ascii=False, encoding="utf-8"))


with codecs.open(titlesFile, 'w', encoding='utf-8') as f:
    f.write(json.dumps(libraryTITLE, indent=4, ensure_ascii=False, encoding="utf-8"))

with codecs.open(conflictsFile, 'w', encoding='utf-8') as f:

    f.write(json.dumps(conflicts.items(), indent=4, ensure_ascii=False, encoding="utf-8"))



