import dns.resolver
import requests
from bs4 import BeautifulSoup

resolver = dns.resolver.Resolver()
resolver.nameservers = ['1.1.1.1', '8.8.8.8', ]
answer = resolver.resolve('torrentgalaxy.to', 'A')


def getItemsTorrentGalaxy(query, queue):
    url = f"https://{answer[0].to_text()}/torrents.php?search={query.replace(' ', '+')}&sort=seeders&order=desc&page=0"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": "https://torrentgalaxy.to/", "Host": "torrentgalaxy.to"
    }
    print(url)
    try:
        response = requests.get(url, timeout=5, headers=headers, verify=False)
        if response.status_code == 200:
            doc = BeautifulSoup(response.content, 'html.parser')
            links = doc.select("div.tgxtablerow")
            if len(links) == 0 and doc.text:
                queue.put( [["None", "", "", "", "", "", "", 0, 0, ""]])
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

                item_list.append(
                    [item_type, lang, title, item_link, uploader, date, size, int(seeds.replace(',', '')),
                     int(leeches.replace(',', '')), magnet])
            queue.put(item_list)
        else:
            print(f"Request returned status code: {response.status_code}")
            queue.put([["None", "", "", "", "", "", "", 0, 0, ""]])
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
