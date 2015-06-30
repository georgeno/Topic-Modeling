__author__ = 'George'
import sys
from tkinter import *
import tkinter as tk
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageTk #for imaging and using word clouds
import mysql, mysql.connector
import re

def connect_to_database():
    cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='documents', buffered=True)
    return cnx, cnx.cursor()

cnx,cursor = connect_to_database()

#creating the object of myInterface

myInterface= Tk()

#setting our String Variable since we are searching for a word.
myWord = StringVar()
#Creating our window and setting it to the size/place on screen requested.
myInterface.geometry('1920x1080') #600 from the top left corner to the right and 250 from the top left corner down
#Setting the title of the search box
myInterface.title('Search')



def firstImageRetrieveDocs(topic):  #if first image gets clicked
    #pass
    #retrieve + display docs from topic prop, 3 highest maybe
    #para3=topic
    newlabel= Label(myInterface,text=topic).place(x=1000, y=600)
    #docidImage1=cursor.execute("SELECT file_id  FROM topic_proportion WHERE topic_id = '%s' LIMIT 2;" %para3)
    #docsid= cursor.fetchall()
    #newlabel= Label(myInterface,text=docsid).place(x=1000, y=600)
    #return



def secondImageRetrieveDocs(topic): #if second image gets clicked
    pass
    #para4=topic
    #newlabel= Label(myInterface,text=topic).place(x=1450, y=800)
    #docidImage2=cursor.execute("SELECT file_id  FROM topic_proportion WHERE topic_id = '%s' LIMIT 2;" %para4)
    #docsid2= cursor.fetchall()
    #newlabel2= Label(myInterface,text=docsid2).place(x=1080, y=600)


def WordCloud():
#getting the value of MyWord which is what we type in the search and storing it in word
    word= myWord.get()
#search the database for the word we entered and return its id, #row includes the results of the query.
    para=word
    wordid=cursor.execute("SELECT id FROM words WHERE word = '%s';" %para)
    row=cursor.fetchall()

#A small test to check if the id is returned correctly
    #newlabel= Label(myInterface,text=row).place(x=200, y=200)

#Using the id of the words, extract the topic ids related to that word
    #row=row.str()
    row=''.join(str(r) for r in row)    #coverting our tuple to string so we can compare the id later
    #row=[int(s) for s in row.split() if s.isdigit()]
    #row= ' '.join(map(row, ()))
    row=row.strip('()')             #getting rid of the parantheses that are left
    row=row.strip(',')              #getting rid of commas
    para2=row

#I want to limit the results to 2 topics max per search.

    topics_ids=cursor.execute("SELECT topic_id FROM topic_words WHERE word_id = '%s' LIMIT 2;" %para2)
    result=cursor.fetchall()

#A small test to check if the topic_id is returned correctly
    #newlabel= Label(myInterface,text=result).place(x=200, y=200)
    result=''.join(str(r) for r in result)
    result=result.strip('()')

    #getting rid of mid brackets
    rem= ')('
    result=result.translate(result.maketrans(dict.fromkeys(rem)))

    #result=result.strip(',(')
    result=result.strip(',')        #last comma getting rid of it
    #newlabel= Label(myInterface,text=result).place(x=200, y=200)

#placing the 2 topic vaues in a list.
    topicList=result.split(",")

#testing list values
    #newlabel= Label(myInterface,text=topicList).place(x=200, y=200)


#get the word clouds with the topic_id values in the interface.
#loop the list, take the values one by one, loop directory and check if matches the name of the pic, if so return the pic
    files=[ f for f in listdir("F:\WordClouds") if isfile(join("F:\WordClouds",f))]
    counter=0;
    for topicId in topicList:
        for f in files:
            if topicId + ".png" == f:
                if counter==0:
                     load= Image.open("F:\WordClouds\\" + f)
                     render=ImageTk.PhotoImage(load)
                     #newlabel= Label(myInterface,text=topicId).place(x=1100, y=600)  #topic id = 5 for geology
                     img= Button(myInterface, image=render, command= lambda topicId=topicId: firstImageRetrieveDocs(topicId))  #making my Image clickable
                     # + sending the function the topic Id of this specific image, topicId=topicId is needed to pass the correct value (scope)
                     img.image=render
                     img.place(x=0,y=100)
                     #newlabel2= Label(myInterface,text=topicId).place(x=1080, y=600)
                     counter=counter+1


                else:
                     load= Image.open("F:\WordClouds\\" + f)
                     render=ImageTk.PhotoImage(load)
                     img= Button(myInterface, image=render, command= lambda topicId=topicId: secondImageRetrieveDocs(topicId))
                     img.image=render
                     img.place(x=1200,y=100) #keep y=100 because we are not interested of going down more in the interface but just move to the side by around 1200
                     #newlabel2= Label(myInterface,text=topicId).place(x=1180, y=600)


# Creating a label and setting its position

myLabel= Label(text='Search Box', fg= 'red', bg= 'yellow').place(x=960, y=70)

#Creating a button

myButton= Button(text='OK', command=WordCloud, fg= 'red', bg='yellow').place(x=980, y=130)

#Adding a text box

myTextBox= Entry(myInterface,text=myWord).place(x=930 , y=100)

#Pass our variable which is search to the function up upon clicking the button that we have.
myInterface.mainloop() 

