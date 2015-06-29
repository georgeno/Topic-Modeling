from pytagcloud import create_tag_image, make_tags
import mysql, mysql.connector
import sys, codecs, re, os, logging, random, time

def init_logger():
    log_formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(log_formatter)
    root_logger.addHandler(console_handler)

def connect_to_database():
    cnx = mysql.connector.connect(user='root', password='',
                              host='127.0.0.1',
                              database='documents', buffered=True)
    return cnx, cnx.cursor()

init_logger()

cnx, cursor = connect_to_database()
		
for tid in range(400):
    sql = "SELECT * FROM (SELECT w.word as w, count(*) as num FROM topic_state ts \
JOIN words w ON w.id = ts.word_id \
WHERE ts.word_id IN (SELECT word_id FROM topic_words WHERE topic_id = %d) \
AND ts.topic_id = %d \
GROUP BY word) s \
ORDER BY num DESC" % (tid, tid)
    cursor.execute(sql)
    counts = cursor.fetchall()
    max = 275000
    for idx in range(len(counts)):
        w, c = counts[idx]
        c = max
        counts[idx] = (w, c)
        max -= 15000
    logging.info("Counts for topic " + str(tid) + ": " + str(counts))
    tags = make_tags(counts, maxsize=80)
    create_tag_image(tags, 'F:\\tmp5\\' + str(tid) + '.png', size=(900, 600), fontname='PT Sans Regular')
    logging.info("Image created")

commit_and_close(cnx, cursor)