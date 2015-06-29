__author__ = 'George'

import os, codecs, json, re, datetime, shutil, itertools, pickle
from collections import Counter
from itertools import chain


def getStopList(lang):
    global STOPFILE_ENG, STOPFILE_HEB
    stoplist = []
    if lang == 'eng':
        with open(STOPFILE_ENG, 'r') as f:
            stoplist = [i.strip() for i in f.read().splitlines()]
    elif lang == 'heb':
        with open(STOPFILE_HEB, 'r', encoding='utf-8') as f:
            stoplist = [i.strip() for i in f.read().splitlines()]
    return stoplist


def initLists():
    global wordlist, symbols_remove, stoplist, wordlist
    wordlist = []
    stoplist_eng = getStopList('eng')
    stoplist_heb = getStopList('heb')
    stoplist = stoplist_eng + stoplist_heb
    symbols_remove = ['$$a', '$$b', '$$c', '$$d', '$$e', '$$f', '$$g', '$$h', '$$j', '$$k', '$$l', '$$m', '$$n', '$$o',
                      '$$p', '$$q',
                      '$$r', '$$s', '$$t', '$$u', '$$v', '$$x', '$$y', '$$z', '$$0', '$$2', '$$3', '$$4', '$$6', '$$8',
                      '(', ')', '...', '[', ']', '?',
                      '!', ',', ';', '"', '.', '&', '/', '\\', '<', '>', '^', '@', '#', '\'s']

def getJsonFilesCached(files_cache):
    with open(files_cache, "rb") as pfile:
        return pickle.load(pfile)


def getJsonFilesNonCached():
    global LIBRARY_PATH, DEFAULT_FILES_CACHE
    json_files = []
    for f in os.listdir(LIBRARY_PATH):
        print(f)
        if dir(f):
            print(f + " is a directory")
            file_path = os.path.join(LIBRARY_PATH, f)
            json_files.append({'dir': file_path, 'files': os.listdir(file_path)})
        else:
            print(f + " is a file")
            json_files.append({'dir': LIBRARY_PATH, 'files': f})
    with open(DEFAULT_FILES_CACHE, "wb") as pfile:
        pickle.dump(json_files, pfile)
    return json_files


def getJsonFiles(files_cache = None):
    total_count = 0;
    start_time = datetime.datetime.now()
    if files_cache is not None:
        json_files = getJsonFilesCached(files_cache)
    else:
        json_files = getJsonFilesNonCached()
    end_time = datetime.datetime.now()
    for dict in json_files:
        total_count += len(dict['files'])
    print(("Total file count: %d in %d minutes") % (total_count, (end_time - start_time).total_seconds() / 60))
    return [json_files, total_count]


def getStoplistRegexPattern(stoplist):
    return r'\b(' + r'|'.join(stoplist) + r')\b\s*'


def getSymbolsRemoveRegexPattern(symbols):
    return r'(' + r'|'.join([re.escape(s) for s in symbols]) + r')'


def compileRegexPatterns(stoplist, symbols_remove):
    print("Compiling regex patterns ...")
    stoplist_pattern = getStoplistRegexPattern(stoplist)
    symbols_pattern = getSymbolsRemoveRegexPattern(symbols_remove)
    extra_cleanup = r'\.-+|\s+-|-\s+|\s+-\s+|^-|-$|\*.*?\:|\*'
    remove_spaces = r'\s+'

    print("Stoplist regex pattern: " + stoplist_pattern)
    print("Symbols regex pattern: " + symbols_pattern)
    return [
        [re.compile(symbols_pattern), ""],
        [re.compile(stoplist_pattern, re.IGNORECASE), " "],
        [re.compile(extra_cleanup), " "],
        [re.compile(remove_spaces), " "]
    ]


def cleanString(str, regex_patterns):
    for pattern, sub in regex_patterns:
        str = pattern.sub(sub, str)
    return str.strip()


def cleanStrings(str_list, regex_patterns):
    new_str_list = []
    for s in str_list:
        print("[BEF] " + s)
        s = cleanString(s, regex_patterns)
        print("[AFT] " + s)
        new_str_list.append(s)
    return new_str_list


def updateWordListFile():
    global wordlist, pfcount, NEW_PATH
    counts = Counter(chain.from_iterable(l for l in wordlist))
    print("Parsed %d files. Printing frequency list to file." % pfcount)
    with codecs.open(os.path.join(NEW_PATH, 'frequency_list.txt'), 'w', encoding='utf-8') as fd:
        print(counts, file=fd)  # prints dictionary to file


def parseFile(dir, file):
    global pfcount
    with codecs.open(os.path.join(dir, file), 'rb', encoding='utf-8') as fi:
        json_data = json.load(fi)
        lang = json_data['language']
        if lang != "eng" and lang != "heb":
            print("Language is not hebrew or english, or not specified. Skipping ...")
            return ['', []]
    pfcount += 1
    return [lang, json_data]


def createNewFilePath(dir, file, lang):
    new_file = file.replace('.json', '.txt')  # replacing json files with txt files
    new_dir = os.path.join(dir + "\\" + lang)  # this is the new directory where I will have my LDA data
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    return [new_dir, new_file]


#########################################################################
# MAIN PROGRAM HERE												#
#########################################################################

LIBRARY_PATH = 'D://MyJsonData'  #Path where my original json data for each book is found.
NEW_PATH = 'C://Output'  #Path where my parsed data will be ready for each book.
STOPFILE_ENG = 'C://Users//George//Desktop//Stopwords//English.txt'  #my english stopwords file
STOPFILE_HEB = 'C://Users//George//Desktop//Stopwords//Hebrew.txt'  #my hebrew stopwords file
DEFAULT_FILES_CACHE = "D://MyJsonData//files_cache.bin"

if os.path.isfile(DEFAULT_FILES_CACHE):
    print("File cache exists. Fetching ...")
    json_files, total_count = getJsonFiles(DEFAULT_FILES_CACHE)
else:
    print("File cache does not exist. Getting the files the good old way ...")
    json_files, total_count = getJsonFiles()

initLists()
regex_patterns = compileRegexPatterns(stoplist, symbols_remove)
print(regex_patterns)

pfcount = 0
fcount = total_count
start_time = datetime.datetime.now()
for file_dict in json_files:
    for file in (f for f in file_dict['files'] if f.endswith('.json')):
        print("\n[%07d] Parsing file '%s'" % (pfcount, file))
        lang, json_data = parseFile(file_dict['dir'], file)
        if len(json_data) == 0:
            continue
        out_str = '\r\n'.join(cleanStrings([json_data['title']], regex_patterns)
                              + cleanStrings(json_data['subjects'], regex_patterns)
                              + cleanStrings(json_data['comments'], regex_patterns)
                              + cleanStrings(json_data['subtitle'], regex_patterns)).lower()

        wordlist.append(out_str.split())

        if pfcount % 1000 == 0:
            updateWordListFile()

        new_dir, new_file = createNewFilePath(NEW_PATH, file, lang)
        with codecs.open(os.path.join(new_dir, new_file), 'w', encoding='utf-8') as fd:
            print("Writing the following to file '" + new_file + "':\r\n" + out_str)
            print(out_str, file=fd)

updateWordListFile()
end_time = datetime.datetime.now()
print("\n%d/%d files parsed in %d minutes.\n" % (pfcount, fcount, (end_time - start_time).total_seconds() / 60))

