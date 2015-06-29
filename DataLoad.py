import mysql, mysql.connector
import sys, codecs, re, os, logging, random, time


def init_logger():
    log_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("DataLoad.log")
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)


def get_file_contents(filename):
    global LIBRARY_PATH
    filename = os.path.basename(filename)
    dir = filename.strip()[0].capitalize() + "_dir"
    fpath = os.path.join(LIBRARY_PATH, dir, filename.replace(".txt", ".json"))
    with codecs.open(fpath, 'r', encoding='utf-8') as fd:
        content = fd.read()
    return fpath, content


def connect_to_database():
    cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='documents', buffered=True)
    return cnx, cnx.cursor()


def commit_and_close(cnx, cursor):
    cnx.commit()
    cursor.close()
    cnx.close()


def insert_data(data, cursor):

    if data[1] is not None and data[2] is not None:
        sql = "INSERT INTO files (id, file_name, content) \
            VALUES (%s, %s, %s)"
        vals = [data[0], data[1], data[2]]
        exec_sql_data(sql, vals, cursor)

    if data[3] is not None and data[4] is not None:
        sql = "INSERT INTO words (id, word) \
            VALUES (%s, %s)"
        vals = [data[3], data[4]]
        exec_sql_data(sql, vals, cursor)

    if data[0] is not None and data[3] is not None and data[5] is not None:
        sql = "INSERT INTO topic_state (file_id, word_id, topic_id) \
            VALUES (%s, %s, %s)"
        vals = [data[0], data[3], data[5]]
        exec_sql_data(sql, vals, cursor)


def exec_sql_data(sql, vals, cursor):
    logging.info("Executing query '" + sql + "' with data '" + str(vals) + "'")
    try:
        cursor.execute(sql, vals)
    except Exception as e:
        logging.error("Failure encountered: " + e.__str__())


def check_id_exists(id, cursor):
    sql = "SELECT * FROM files WHERE id = %s"
    cursor.execute(sql, [id])
    if len(cursor.fetchall()) > 0:
        return True
    return False


def check_fid_exists_dict(fid):
    global fids
    try:
        return fids[fid]
    except Exception as e:
        pass
    return False


def check_wid_exists_dict(wid):
    global wids
    try:
        return wids[wid]
    except Exception as e:
        pass
    return False


# Prepare logger
#logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')
init_logger()

LIBRARY_PATH = 'D:\\MyJsonData'
TOPIC_STATE = 'F:\\mallet-2.0.7\\topic-state'
TUTORIAL_KEYS = 'F:\\mallet-2.0.7\\tutorial_keys.txt'

# Regex pattern
regex_pattern = r'^\s*(?P<fid>\d+)\s+(?P<fname>.*?\.txt)\s+(?P<wnum>\d+)\s+(?P<wid>\d+)\s+(?P<word>.*?)\s+(?P<tid>\d+)\s*$'
compiled_pattern = re.compile(regex_pattern)

# Connect to database
cnx, cursor = connect_to_database()

fids = {}
wids = {}
ids_max_len = 10000
rate = 0
last = time.time()

cur = 0
start_from = 26548728		#dc, had to resume from here

for line in codecs.open(TOPIC_STATE, 'r', encoding='utf-8'):
    cur += 1
    line = line.strip()

    if line.startswith('#') or cur < start_from:
        continue

    m = compiled_pattern.match(line)

    if m is not None:
        logging.info(line + ", [" + str(cur) + "]")

        fid = m.group('fid')
        fname = m.group('fname')
        wid = m.group('wid')
        word = m.group('word')
        tid = m.group('tid')
        fpath = None
        content = None

        if check_fid_exists_dict(fid) is False:
            logging.info("File ID " + fid + " does not exist in memory")
            try:
                fpath, content = get_file_contents(fname)
            except Exception as e:
                logging.error("Failure encountered: " + e.__str__())

        if check_wid_exists_dict(wid) is True:
            logging.info("Word ID " + wid + " already exists in memory")
            word = None

        data = [fid, fpath, content, wid, word, tid]
        logging.info(data)

        try:
            insert_data(data, cursor)
            if len(fids) > ids_max_len:
                rate = (ids_max_len / (time.time() - last)) * 60
                last = time.time()
                fids = {}
            if len(wids) > ids_max_len:
                wids = {}
            fids[fid] = True
            wids[wid] = True
            if random.random() > 0.99:
                logging.info("Rolled above 99%. Committing changes to database.")
                cnx.commit()
        except Exception as e:
            logging.error("Failure encountered: " + e.__str__())

commit_and_close(cnx, cursor)
