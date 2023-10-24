"""
Index the LVE repository into a sqlite database.
"""
import sqlite3
import os
import time
import json
from lve.lve import LVE
from tqdm import tqdm

class LVEIndex:
    def __init__(self, file="lves.db"):
        # delete old database
        if os.path.exists(file):
            os.remove(file)

        self.curs = sqlite3.connect(file).cursor()        
        self.prepare()

    def prepare(self):
        # table of LVEs
        self.curs.execute("""CREATE TABLE IF NOT EXISTS lves (
            name TEXT,
            category TEXT,
            author TEXT,
            updated DATETIME,
            model TEXT,
            path TEXT,
            instance_files TEXT
        )""")

        # table of instances
        self.curs.execute("""CREATE TABLE IF NOT EXISTS instances (
            lve TEXT REFERENCES lves(name),
            file TEXT,
            created DATETIME,
            passed BOOLEAN,
            author TEXT
        )""")

    def build(self):
        # get all test.json files traversing ../repository recursively
        test_files = []

        for root, dirs, files in os.walk("../../repository"):
            for file in files:
                if file.endswith("test.json"):
                    test_files.append(os.path.join(root, file))
        
        categories = set()

        # for each test.json file get last commit and build site
        for t in tqdm(test_files, desc="Indexing LVEs"):
            lve = LVE.from_path(os.path.dirname(t))
            categories.add(lve.category)

            stime = lve.last_updated()
            
            # add LVE table entries
            self.curs.execute("""INSERT INTO lves VALUES (?, ?, ?, ?, ?, ?, ?)""", (
                lve.name,
                lve.category,
                lve.author,
                time.strftime("%Y-%m-%d %H:%M:%S", stime),
                lve.model,
                lve.path,
                "\n".join(lve.instance_files)
            ))

            for f in lve.instance_files:
                instance_file_path = os.path.join(lve.path, "instances", f)
                with open(instance_file_path, 'r') as file:
                    for i, line in enumerate(file.readlines()):
                        line = json.loads(line)
                        instance_time = line.get("run_info", {}).get("timestamp", "Thu Jan 1 00:00:00 1970")
                        self.curs.execute("""INSERT INTO instances VALUES (?, ?, ?, ?, ?)""", (
                            lve.path,
                            f + ":" + str(i),
                            time.strftime("%Y-%m-%d %H:%M:%S", time.strptime(instance_time, "%a %b %d %H:%M:%S %Y")),
                            line.get("passed", line.get("is_safe", False)),
                            line.get("author", "Anonymous")
                        ))

    def print_names(self):
        # print all LVE names
        for l in self.curs.execute("""SELECT name, author FROM lves"""):
            print(l)

    def print_instances(self):
        # print all instances
        for i in self.curs.execute("""SELECT * FROM instances"""):
            print(i)

    def combined_score(self, timespan="-14 day"):
        instance_scores = f"""SELECT author, COUNT(*) as count FROM instances WHERE created > datetime('now', '{timespan}') GROUP BY author ORDER BY COUNT(*) DESC"""
        lve_scores = f"""SELECT author, COUNT(*) as count FROM lves WHERE updated > datetime('now', '{timespan}') GROUP BY author ORDER BY COUNT(*) DESC"""
        # join instance and lve author stats (sum, assume 0 if not in one)
        combined = """SELECT (CASE WHEN i.author IS NULL THEN l.author ELSE i.author END) AS author, i.count as instance_count, l.count as lve_count FROM ({}) AS i FULL OUTER JOIN ({}) AS l ON i.author = l.author ORDER BY i.count + l.count DESC""".format(instance_scores, lve_scores)
        # sum i.count and l.count, assume 0 if not in one
        summed = """SELECT author, CASE WHEN instance_count IS NULL THEN 0 ELSE instance_count END + CASE WHEN lve_count IS NULL THEN 0 ELSE lve_count END as count FROM ({}) ORDER BY count DESC""".format(combined)
        
        ranking = []

        for author, score in self.curs.execute(summed):
            if author is None or author == "Anonymous" or len(author) == 0:
                continue
            ranking.append((author, score))
        
        return ranking

if __name__ == '__main__':
    index = LVEIndex()
    index.build()

    index.combined_score()