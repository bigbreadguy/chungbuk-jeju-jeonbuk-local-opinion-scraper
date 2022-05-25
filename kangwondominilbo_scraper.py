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

    article = soup.find(id="article-view-content-div").find("p").get_text()

    return article

def get_article_list(page_num:int):
    url_base = f"https://www.kado.net/news/articleList.html?page={page_num}&box_idxno=&sc_sub_section_code=S2N83&view_type=sm"
    response = get_response(url_base)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")

    section_list = soup.find(id="section_list")
    article_list = soup.find(class_="type2").find_all("li")

    is_done = False
    titles = []
    urls = []
    summaries = []
    bylines_0 = []
    bylines_1 = []
    bylines_2 = []
    articles = []
    for content in article_list:
        h4 = content.find(class_="titles")
        title = h4.find("a").get_text()
        url = "https://www.kado.net/" + h4.find("a").get("href")
        summary = content.find(class_="lead line-6x2").get_text()
        bylines = content.find(class_="byline").split(" | ")
        byline_0 = bylines[0]
        byline_1 = bylines[1]
        byline_2 = bylines[2]
        article = get_paragraph(url)

        date = datetime.datetime.strptime(byline_2, "%Y.%m.%d")
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

    result_dir = os.path.join("./result", "kangwondominilbo")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    page_num = 1

    while True:
        result_df, is_done = get_article_list(page_num)
        result_df.to_csv(os.path.join(result_dir, f"kangwondominilbo_opinions_p{page_num}.csv"), encoding="utf-8-sig")
        print(f"{page_num} 페이지 스크랩 완료")

        if is_done:
            break

        page_num+=1