import json

def getCode(elt):
    # print("code is " + elt.split(' ')[0])
    return elt.split(' ')[0]


def getValue(elt):
    return ' '.join(elt.split(' ')[4:])


def getTitle(elt):
    title=' '.join(elt.split()[2:]).split('/$$c')
    return(title)


def isbnOfBookInLib(title,lib):
    books=lib.values()
    for book in books:
        if book['title'] == title:
            return(book['isbn'])


def addBookToLib(bookInst,allBooks):
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

        elif value <> book2[feature]:
            if not value:
                book1[feature]=book2[feature]
            elif not book2[feature]:
                continue
            else:
                book1['conflicts'].append([feature, value, book2[feature]])
    return(book1)


def makebook():
    return ({"isbn":"",
          "title":"",
          "subtitle":[],
          "format":"",
          "serialNum":[],
          "editors":[],
          "subjects":[],
          "authors":[],
          "titleAdditions":[],
          "authorDates":[],
          "language":"",
          "publisher":[],
          "physical":[],
          "comments":[],
          "dewey":"",
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
            title=getTitle(elt)
            mainTitle=title[0].split('$$b')
            #print(mainTitle[0].split('$$h')[0][3:])
            bookInst['title']=mainTitle[0].split('$$h')[0][3:].rstrip(' .,;/:')
            if len(title)>1:
                bookInst['titleAdditions'].extend(title[1:])
            if len(mainTitle)>1:
                bookInst['subtitle']=mainTitle[1:]

        elif code.startswith("6"):#code == '650' or code=='695' or code=='6000' or '60014'':
            bookInst['subjects'].append(' '.join(elt.split(' ')[3:])[3:].rstrip('.,/;:'))
        elif code == '020':
            bookInst['isbn']=getValue(elt).split(' ')[0][3:]
        elif code == '041':
            bookInst['language']=getValue(elt)[3:]
        elif code=="260":
            bookInst['publisher'].append(getValue(elt).rstrip(' ,.;-/:'))
        elif code == "300":
            bookInst['physical'].append(getValue(elt).rstrip(' ,.;-/:'))
        elif code.startswith("5"):
            bookInst['comments'].append(getValue(elt).rstrip(' ,.;-/:'))

    #print(book)
    return(bookInst)


newRecord=True
thisBook=[]
currentBook = dict()
#currentBook['FMT']='BK'
allBooks = {}


with open('C://Users//George//Desktop//ULI//Marc_Data//sample.marc', 'rb') as fh:
    #reader = MARCReader(fh)

    for line in fh: #must make a record from each field
        lineElts =line.split(' ')
        if newRecord:
            bookSerial = lineElts[0]
            #print(bookSerial)
            thisBook.append(line[10:].rstrip('\n'))
            newRecord=False

        elif bookSerial == lineElts[0]: #not a new book
            thisBook.append(line[10:].rstrip('\n'))

        elif bookSerial is not lineElts[0]: #new book
            bookSerial = lineElts[0]
            #printBookInst(bookInstance(thisBook))
            #pprint.pprint(bookInstance(thisBook))
            newRecord=True
            #allBooks.append(bookInstance(thisBook))
            allBooks=addBookToLib(bookInstance(thisBook),allBooks)
            thisBook=[line[10:].rstrip('\n')]
            #booksCounter+=1

data=json.dumps(allBooks, indent=4, ensure_ascii=False)
print data





