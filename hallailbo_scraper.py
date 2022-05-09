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

    bylines = soup.find(id="byline").find_all("li")
    byline_0 = bylines[0].get_text()
    byline_1 = bylines[1].get_text()

    article = soup.find(class_="cont_gisa").find(class_="article_txt").get_text()

    return byline_0, byline_1, article

def is_before_2018(byline:str):
    year_str = byline.split("입력 : ")[-1].split("(")[0]
    date = datetime.datetime.strptime(year_str, "%Y. %m.%d")

    return date < datetime.datetime(2018, 5, 1)

def get_article_list(page_num:int):
    url_base = f"http://www.ihalla.com/section.php?sid=43&page={page_num}"
    response = get_response(url_base)
    
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    
    article_list = soup.find(class_="container").find(class_="cont_left")
    article_divs = article_list.find_all("div")
    
    is_done = False
    titles = []
    urls = []
    summaries = []
    bylines_0 = []
    bylines_1 = []
    articles = []
    for article_div in article_divs:
        divs = article_div.find_all("div")
        if len(divs) > 0:
            for div in divs:
                a = div.find("a")
                if a is not None:
                    titles.append(a.get_text())
                    
                    url = "http://www.ihalla.com" + a.get("href")
                    urls.append(url)

                    byline_0, byline_1, article = get_paragraph(url)
                    is_done = is_before_2018(byline_0)

                    if is_done:
                        break

                    bylines_0.append(byline_0)
                    bylines_1.append(byline_1)
                    articles.append(article)

            p = article_div.find("p")
            summaries.append(p.get_text())

    result = pd.DataFrame(
                data = {
                    "titles": titles,
                    "urls": urls,
                    "summaries": summaries,
                    "bylines_0": bylines_0,
                    "bylines_1": bylines_1,
                    "articles": articles,
                    }
            )

    return result, is_done

if __name__ == "__main__":
    if not os.path.exists("./result"):
        os.makedirs("./result")

    result_dir = os.path.join("./result", "hallailbo")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)

    page_num = 1

    while True:
        result_df, is_done = get_article_list(page_num)
        
        if is_done:
            break

        result_df.to_csv(os.path.join(result_dir, f"hallailbo_opinions_p{page_num}.csv"), encoding="utf-8-sig")
        print(f"{page_num} 페이지 스크랩 완료")
        page_num+=1