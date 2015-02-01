__author__ = 'George'

import json
import codecs
import os


src_dir='C:/Users/George/Desktop/JsonForEachBook/Jsons' #1
for f in os.listdir(src_dir): #2
    file_name=os.path.join(src_dir,f) #3

    with codecs.open(file_name,'r+', encoding='utf-8') as fi: #4
        json_data=json.load(fi) #7
        select_subject=json_data['subjects'] #8
        select_isbn=json_data['isbn']   #9
        fs=open((f.rsplit(".",1)[0])+".txt",'w',encoding='utf-8') #first file is created which has the number of the first isbn #14
        print(select_subject,file=fs)#16
        print('\n') #13

