from enum import verify

import dns.resolver
import httpx
import requests
from bs4 import BeautifulSoup

resolver = dns.resolver.Resolver()
resolver.nameservers = ['1.1.1.1', '8.8.8.8', ]
answer = resolver.resolve('torrentquest.com', 'A')


def getItemsTorrentQuest(query, page=1):
    url = f"https://{answer[0].to_text()}/{query[0]}/{query}/se/desc/{page}/"
    headers = {
        "User-Agent": "Mozilla/5.0", "Referer": "https://torrentquest.com/", "Host": "torrentquest.com"}
    print(url)
    try:
        with httpx.Client(verify=False) as client:  # Disable SSL verification if necessary
            response = client.get(url, headers=headers, timeout=5)
            print(response.text)
        response.raise_for_status()
        if response.status_code == 200:
            doc = BeautifulSoup(response.content, 'html.parser')
            print(doc)
            links = doc.select("div.tgxtablerow")
            if len(links) == 0 and doc.text:
                return [["None", "", "", "", "", "", "", 0, 0, ""]]
            item_list = []
            for link in links:
                item_type = link.contents[1].text.split()[0]
                lang = link.contents[3].find("img").get("title")
                title = link.contents[4].find("a").get("title")
                item_link = "https://www.torrentgalaxy.to" + link.contents[4].find("a").get("href")
                uploader = link.contents[7].text
                date = link.contents[12].text
                size = link.contents[8].text
                seedleeches = link.contents[11].text.split('/')
                seeds = seedleeches[0][1::]
                leeches = seedleeches[1][0:-1:]
                magnet = link.contents[5].select_one("a[href*=magnet]").get("href")

                item_list.append([item_type, lang, title, item_link, uploader, date, size, seeds, leeches, magnet])
            return item_list
        else:
            print(f"Request returned status code: {response.status_code}")
            return [["None", "", "", "", "", "", "", 0, 0, ""]]
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


print(getItemsTorrentQuest("bully", 1))
