#!/usr/bin/env python
import os
import yaml
import ssl
import psycopg2
import psycopg2.extras
import re
from boto.s3.connection import S3Connection

rds_credentials = yaml.load(open(os.path.expanduser('~/aws_rds_cred.yml')))

conn = S3Connection()


def main(rds_credentials, conn):

    DB_NAME = rds_credentials['final_project_postgres']['dbname']
    DB_USER = rds_credentials['final_project_postgres']['user']
    DB_HOST = rds_credentials['final_project_postgres']['host']
    DB_PASSWORD = rds_credentials['final_project_postgres']['password']

    data_bucket = conn.get_bucket('dsci6007-final-project-3nf')

    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

        try:
            conn = psycopg2.connect("dbname='" + DB_NAME + "' user='" +
                                    DB_USER +
                                    "' host='" + DB_HOST +
                                    "' password='" + DB_PASSWORD + "'")
        except:
            print("Unable to connect to the database in RDS.")

    cur = conn.cursor()

    try:
        i = 0
        for key in data_bucket.list():
            # topic
            if re.match(r"topic_table/topic_table.csv", key.name):
                if re.findall(r"part-", key.name) and key.size > 0:
                    data_key = data_bucket.get_key(key)
                    data = data_key.get_contents_as_string()
                    data = data.split("\n")
                    for items in data:
                        elements = items.split(",")
                        if elements[0]:
                            id = int(elements[0])
                            elements[1] = re.sub("'", '', elements[1])
                            elements[2] = re.sub("'", '', elements[2])
                            name = elements[1]
                            url = elements[2]

                            cur.execute("INSERT INTO topic (topic_id, topic_name, topic_urlkey)\
                                VALUES({}, '{}', '{}') ON CONFLICT DO NOTHING".format(id, name, url))
                            i += 1
                            # We commit inserts every 100 items.
                            if i % 100 == 0:
                                conn.commit()
            # category
            j = 0
            if re.match(r"category_table/category_table.csv", key.name):
                if re.findall(r"part-", key.name) and key.size > 0:
                    data_key = data_bucket.get_key(key)
                    data = data_key.get_contents_as_string()
                    data = data.split("\n")
                    for items in data:
                        elements = items.split(",")
                        if elements[0]:
                            id = int(elements[0])
                            elements[1] = re.sub("'", '', elements[1])
                            elements[2] = re.sub("'", '', elements[2])
                            short_name = elements[1]
                            name = elements[2]

                            cur.execute("INSERT INTO category (category_id, category_shortname, category_name)\
                                VALUES({}, '{}', '{}') ON CONFLICT DO NOTHING".format(id, short_name, name))

                            j += 1
                            # We commit inserts every 100 items.
                            if j % 100 == 0:
                                conn.commit()

            # organizer
            k = 0
            if re.match(r"organizer_table/organizer_table.csv", key.name):
                if re.findall(r"part-", key.name) and key.size > 0:
                    data_key = data_bucket.get_key(key)
                    data = data_key.get_contents_as_string()
                    data = data.split("\n")
                    for items in data:
                        elements = items.split(",")
                        if elements[0]:
                            id = int(elements[0])
                            elements[1] = re.sub("'", '', elements[1])
                            name = elements[1]

                            cur.execute("INSERT INTO member (member_id, member_name)\
                                VALUES({}, '{}') ON CONFLICT DO NOTHING".format(id, name))

                            k += 1
                            # We commit inserts every 100 items.
                            if k % 100 == 0:
                                conn.commit()
    except:
        print("Unable to execute and commit insert statement.")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main(rds_credentials, conn)
