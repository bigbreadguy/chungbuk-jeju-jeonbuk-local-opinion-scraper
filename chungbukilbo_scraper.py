import os
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_response(url:str):
    response = requests.get(url)

    return response

def get_paragraph_bylines(url:str):
    response = get_response(url)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    article_div = soup.find(class_="article")
    b = article_div.find("b").get_text()
    article = article_div.get_text().split(b)[-1]

    bylines = soup.find(class_="art_sum")
    byline_0 = bylines.find("div").find("a").find("b").get_text()
    byline_1 = bylines.find("ul").find_all("li")[-1].get_text()

    return article, byline_0, byline_1

def get_article_list(page_num:int):
    url_base = f"https://www.inews365.com/news/section_list_all.html?sec_no=81&page={page_num}"
    response = get_response(url_base)
    
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    article_list = soup.find(id="alt1").find(class_="art_list")
    list_blocks = article_list.find_all(class_="no_img")

    is_done = False
    titles = []
    urls = []
    summaries = []
    bylines_0 = []
    bylines_1 = []
    articles = []
    for list_block in list_blocks:
        a = list_block.find("a")
        title = a.find("h3").get_text()
        url = "https://www.inews365.com/news/" + a.get("href")
        summary = a.find("p").get_text()
        article, byline_0, byline_1 = get_paragraph_bylines(url)

        date = datetime.datetime.strptime(byline_1, "최종수정%Y.%m.%d %H:%M:%S")
        if date < datetime.datetime(2018, 5, 1):
            is_done = True
            break
        
        titles.append(title)
        urls.append(url)
        summaries.append(summary)
        bylines_0.append(byline_0)
        bylines_1.append(byline_1)
        articles.append(article)
    
    result_df = pd.DataFrame(
        {
            "titles": titles,
            "urls": urls,
            "summaries": summaries,
            "bylines_0": bylines_0,
            "bylines_1": bylines_1,
            "articles": articles,
        }
    )

    return result_df, is_done


if __name__ == "__main__":
    if not os.path.exists("./result"):
        os.makedirs("./result")

    result_dir = os.path.join("./result", "chungbukilbo")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    page_num = 1

    while True:
        result_df, is_done = get_article_list(page_num)
        result_df.to_csv(os.path.join(result_dir, f"chungbukilbo_opinions_p{page_num}.csv"), encoding="utf-8-sig")
        print(f"{page_num} 페이지 스크랩 완료")

        if is_done:
            break

        page_num+=1