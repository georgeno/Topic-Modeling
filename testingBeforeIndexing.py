import json
import codecs

in_file=codecs.open('C:/Users/George/Desktop/1.json','r',encoding='utf-8')
new_dict=json.load(in_file)
in_file.close()
print(new_dict) # testing purposes.
# we can do a normal open to test on english file.
