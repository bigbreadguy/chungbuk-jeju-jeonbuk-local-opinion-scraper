import os
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_response(url:str):
    response = requests.get(url)

    return response

def get_paragraph(url:str):
    response = get_response(url)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    article = soup.find(id="kwNewsBody").get_text()
    date = soup.find(id="newstit").find("ul").find(class_="sub").get_text().split("&nbsp")[0]

    return article, date


def get_article_list(page_num:int):
    url_base = f"http://m.kwnews.co.kr/List.asp?s=301&page={page_num}"
    response = get_response(url_base)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    article_list = soup.find_all(class_="kwList2")
    
    is_done = False
    titles = []
    urls = []
    articles = []
    dates = []
    for content in article_list:
        a = content.find("a")
        url = a.get("href")
        title = a.find("p").get_text().split("[사설]")[-1]
        article, date = get_paragraph(url)

        date = datetime.datetime.strptime(date, "%Y-%m-%d")
        if date < datetime.datetime(2018, 5, 1):
            is_done = True
            break

        titles.append(title)
        urls.append(url)
        articles.append(article)
        dates.append(date)
    
    result_df = pd.DataFrame(
        {
            "titles": titles,
            "urls": urls,
            "articles": articles,
            "dates": dates,
        }
    )

    return result_df, is_done

if __name__ == "__main__":
    if not os.path.exists("./result"):
        os.makedirs("./result")

    result_dir = os.path.join("./result", "kangwonilbo")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    page_num = 1

    while True:
        result_df, is_done = get_article_list(page_num)
        result_df.to_csv(os.path.join(result_dir, f"kangwonilbo_opinions_p{page_num}.csv"), encoding="utf-8-sig")
        print(f"{page_num} 페이지 스크랩 완료")

        if is_done:
            break

        page_num+=1