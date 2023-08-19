import requests
import sys
from threading import Thread
import re
from bs4 import BeautifulSoup as bs
import csv

NUM_WORKERS = 16

num_visited = 0
to_visit = []
visited = set()

law_dict = {}



def explore():
    global num_visited, to_visit, visited
    
    while True:
        if not to_visit:
            return
        
        next = to_visit.pop(0)
        print(str(num_visited).ljust(6) + next)
        visited.add(next)
        num_visited += 1

        r = requests.get(next)
        soup = bs(r.content, "html.parser")
        tab_content = soup.find("div", class_="tab_content")
        if not tab_content:
            continue

        h3 = tab_content.find("h3")
        if h3:
            code = h3.text.split(" ")[-1]
            for div in tab_content.find_all("div", align="left"):
                h6 = div.find("h6")
                if not h6:
                    continue
                section = h6.find("a").text

                law_content = ""
                for p in div.find_all("p"):
                    law_content += p.text + " "
                
                law_dict[code + " " + section] = law_content
            continue

        for anchor in tab_content.find_all("a"):
            href = anchor.get("href")
            if href.find("/faces") != 0:
                continue
            url = "https://leginfo.legislature.ca.gov" + anchor.get("href")
            if url not in visited and url not in to_visit:
                to_visit.append(url)

def make_threads(start_url):
    to_visit.append(start_url)
    threads = []
    for i in range(NUM_WORKERS):
        t = Thread(target=explore)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

def print_dict():
    for identifier in law_dict:
        print(identifier.ljust(15) + ", " + law_dict[identifier])

def save_dict_as_csv():
    with open("id_text.csv", 'w') as csvfile:
        csv.field_size_limit(sys.maxsize)
        writer = csv.writer(csvfile)
        writer.writerow(["id", "text"])
        for identifier in law_dict:
            writer.writerow([identifier, law_dict[identifier]])

def main():
    global visited
    # constitution skipped because of different formatting
    visited.add("https://leginfo.legislature.ca.gov/faces/codesTOCSelected.xhtml?tocCode=CONS&tocTitle=+California+Constitution+-+CONS")
    make_threads("https://leginfo.legislature.ca.gov/faces/codes.xhtml")
    # print_dict()
    save_dict_as_csv()

if __name__ == '__main__':
    main()