from tkinter import *
import tkinter as tk
from os import listdir
from os.path import isfile, join
from PIL import Image, ImageTk #for imaging and using word clouds
import mysql, mysql.connector
import itertools
import re
import os

checktopic=0
def connect_to_database():
    cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='documents', buffered=True)
    return cnx, cnx.cursor()

cnx,cursor = connect_to_database()





class SearchInterface():

    def __init__(self,master):
        frame=Frame(master)
        frame.pack()

        self.searchButton= Button(frame,text="Search",command=self.retrieveWordClouds)
        self.searchButton.pack(side=RIGHT)
        self.quitButton= Button(frame,text='Reset',command=lambda: self.reset())
        self.quitButton.pack(side=LEFT)
        myTextBox= Entry(text=myWord).place(x=900 , y=100)


    def reset(self):    #check before resetting if we have a word at all
        global checktopic
        if checktopic>0:
            python = sys.executable
            os.execl(python, python, * sys.argv)
        mysearch=myWord.get()
        if mysearch:
            newLabel.place_forget()
        else:
            pass


#if left image gets clicked
    def firstImageRetrieveDocs(self,topic):
        #cursor.execute("SELECT files.file_name,files.content FROM topic_proportion join files on file_id = id WHERE topic_id = %s order by proportion desc limit 10" % topic)
        cursor.execute("SELECT file_name, content from (SELECT files.file_name,files.content FROM topic_proportion join files on file_id = id WHERE topic_id = %s order by proportion desc limit 10) tmp group by content" % topic)
        docsid= cursor.fetchall()
        myList=list(itertools.chain(*docsid))
        myString=''.join(myList)
        myNewString=re.findall('"title": "(.+?),',myString)
        myList2=list(itertools.chain(*myNewString))
        myString2=''.join(myList2)
        myString3=myString2.replace('"',"\n") #replacing " with new line (separating books)
        newLabel= Label(text=myString3,font="Times 12").place(x=0, y=700)

#if right image gets clicked
    def secondImageRetrieveDocs(self,topic):
         cursor.execute("SELECT file_name, content from (SELECT files.file_name,files.content FROM topic_proportion join files on file_id = id WHERE topic_id = %s order by proportion desc limit 10) tmp group by content" % topic)
         docsid= cursor.fetchall()
         myList=list(itertools.chain(*docsid))
         myString=''.join(myList)
         myNewString=re.findall('"title": "(.+?),',myString)
         myList2=list(itertools.chain(*myNewString))
         myString2=''.join(myList2)
         myString3=myString2.replace('"',"\n")
         newlabel= Label(text=myString3,font="Times 12").place(x=1300, y=700)

    def retrieveWordClouds(self):
        global checktopic
        global searchWord
        searchWord=""
        global newLabel     #I want to use it in another function (reset) therefore I define it as global.
        global topicId      #I want to use it in another functions upon retrieving results
        searchWord=myWord.get()
        mysearchWord=searchWord
        checkWord=cursor.execute("select count(*) from words join topic_words on id = word_id where word ='%s';" %mysearchWord)
        exists=cursor.fetchall()
        #newLabel=Label(MyInterface,text=exists)
        #newLabel.place(x=1000,y=200)
        newlist=list(itertools.chain(*exists))
        if newlist==[0]:
             newLabel=Label(MyInterface,text='The word you are looking for does not exist in the topics',font="Times 12")
             newLabel.place(x=830,y=150)
        else:
            checktopic+=1
            wordid=cursor.execute("SELECT id FROM words WHERE word = '%s';" %mysearchWord)
            myWordId=cursor.fetchall()
            myWordId=''.join(str(r) for r in myWordId)
            myWordId=myWordId.strip('()')
            myWordId=myWordId.strip(',')
            topics_ids=cursor.execute("SELECT topic_id FROM topic_words WHERE word_id = '%s' LIMIT 2;" %myWordId)
            myTopicId=cursor.fetchall()
            myTopicId=''.join(str(r) for r in myTopicId)
            myTopicId=myTopicId.strip('()')
            rem= ')('
            myTopicId=myTopicId.translate(myTopicId.maketrans(dict.fromkeys(rem)))
            myTopicId=myTopicId.strip(',')
            topicList=myTopicId.split(",")

            #newLabel= Label(MyInterface,text=topicList)
            #newLabel.place(x=830,y=150)

            files=[ f for f in listdir("F:\WordClouds") if isfile(join("F:\WordClouds",f))]
            counter=0;
            for topicId in topicList:
                for f in files:
                    if topicId + ".png" == f:
                        if counter==0:
                             load= Image.open("F:\WordClouds\\" + f)
                             render=ImageTk.PhotoImage(load)
                             img= Button(image=render, command= lambda topicId=topicId: self.firstImageRetrieveDocs(topicId))  #making my Image clickable
                             img.image=render
                             img.place(x=0,y=0)
                             counter=counter+1
                        else:
                            load= Image.open("F:\WordClouds\\" + f)
                            render=ImageTk.PhotoImage(load)
                            img= Button(image=render, command= lambda topicId=topicId: self.secondImageRetrieveDocs(topicId))
                            img.image=render
                            img.place(x=1200,y=0)



MyInterface=Tk()
global myWord       #so I can use upon passing it to the retrieve Word Cloud function
myWord= StringVar()
x=SearchInterface(MyInterface)
MyInterface.geometry("1920x1080")
MyInterface.title('Library Search')



SearchLabel= Label(text='Please Enter Your Search Topic', fg= 'red', bg= 'yellow').place(x=880, y=50)
#myTextBox= Entry(myInterface,text=myWord).place(x=930 , y=100)

MyInterface.mainloop()

