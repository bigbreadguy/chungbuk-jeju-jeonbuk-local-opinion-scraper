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

    paragraphs = soup.find(class_="article_txt_container").find_all("p")

    article = []
    for p in paragraphs:
        article.append(p.get_text())

    return "\n".join(article).split("저작권자 © 전북일보 인터넷신문 무단전재 및 재배포 금지")[0]

def get_article_list(page_num:int):
    url_base = f"https://www.jjan.kr/seriesList/008007?page={page_num}"
    response = get_response(url_base)
    
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    section_list = soup.find(class_="section_list")
    section_news = section_list.find_all(class_="section_news media")

    is_done = False
    titles = []
    urls = []
    summaries = []
    bylines_0 = []
    bylines_1 = []
    bylines_2 = []
    articles = []
    for section in section_news:
        news_body = section.find(class_="media-body news_body")
        a = news_body.find("a")
        title = a.find("h1").get_text()
        url = "https://www.jjan.kr/" + a.get("href")
        summary = a.find("p").get_text()
        bylines = [li.get_text() for li in news_body.find(class_="line_info").find_all("li")]
        byline_0 = bylines[0]
        byline_1 = bylines[1]
        byline_2 = bylines[2]
        article = get_paragraph(url)

        date = datetime.datetime.strptime(byline_2, "%Y.%m.%d %H:%M")
        if date < datetime.datetime(2018, 5, 1):
            is_done = True
            break
        
        titles.append(title)
        urls.append(url)
        summaries.append(summary)
        bylines_0.append(byline_0)
        bylines_1.append(byline_1)
        bylines_2.append(byline_2)
        articles.append(article)
    
    result_df = pd.DataFrame(
        {
            "titles": titles,
            "urls": urls,
            "summaries": summaries,
            "bylines_0": bylines_0,
            "bylines_1": bylines_1,
            "bylines_2": bylines_2,
            "articles": articles,
        }
    )

    return result_df, is_done

if __name__ == "__main__":
    if not os.path.exists("./result"):
        os.makedirs("./result")

    result_dir = os.path.join("./result", "jeonbukilbo")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    page_num = 1

    while True:
        result_df, is_done = get_article_list(page_num)
        result_df.to_csv(os.path.join(result_dir, f"jeonbukilbo_opinions_p{page_num}.csv"), encoding="utf-8-sig")
        print(f"{page_num} 페이지 스크랩 완료")

        if is_done:
            break

        page_num+=1