import requests
from bs4 import BeautifulSoup


def getItemsLimeTorrents(query, page=1):
    url = f"https://www.limetorrents.lol/search/all/{query.replace(' ', '-')}/seeds/{page}/"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, timeout=5, headers=headers)
        if response.status_code == 200:
            doc = BeautifulSoup(response.content, 'html.parser')
            links = doc.select("tr")
            links = links[5::]
            if len(links) == 0 and doc.text:
                return [["None", "", "", "", "", "", "", 0, 0, ""]]
            item_list = []
            for link in links:
                dateType = link.select("td")[1].text.split('-')
                item_type = dateType[1].split(' ')[-1]
                lang = "null"
                title = link.select("td")[0].text
                item_link = "https://limetorrents.lol" + link.select("td")[0].select("a")[1].get("href")
                uploader = "limeTorrents"
                date = dateType[0]
                size = link.select("td")[2].text
                seeds = link.select("td")[3].text
                leeches = link.select("td")[4].text
                magnet = "magnet:?xt=urn:btih:" + link.select("td")[0].find("a").get("href")[29::].split('.')[0]

                item_list.append([item_type, lang, str(title), item_link, uploader, date, size, seeds, leeches, magnet])

            return item_list
        else:
            print(f"Request returned status code: {response.status_code}")
            return [["None", "", "", "", "", "", "", 0, 0, ""]]
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")


print(getItemsLimeTorrents('batman', 1))
