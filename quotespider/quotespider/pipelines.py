# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# db_local
# class db_local(object):
#     def conn_db_local(self):
#         return {'host': 'localhost', 'user': 'root', 'passwd': '', 'database': '',}

import mysql.connector
from .database import db_local
import sys

class QuotespiderPipeline(object):

    def __init__(self):
        self.create_connectin()
        self.create_table()

    def create_connectin(self):
        db = db_local().conn_db_local()


        self.conn = mysql.connector.connect(
            host = db['host'],
            user = db['user'],
            passwd = db['passwd'],
            database = db['database']
        )
        self.curr = self.conn.cursor()

    def create_table(self):
        self.curr.execute("""CREATE TABLE IF NOT EXISTS `quotes_tb` (`id` int not null auto_increment, `title` text, `author` text, `tag` text, primary key (id))""")

    def process_item(self, item, spider):
        self.store_tb(item)
        return item

    def store_tb(self, item):
        try:
            self.curr.execute("""insert into `quotes_tb` (title, author, tag) values (%s, %s, %s) """, (
                item['title'][0],
                item['author'][0],
                item['tag'][0]
            ))
        except mysql.connector.DatabaseError as err:
            print("Error: ", err)
        else:
            self.conn.commit()

