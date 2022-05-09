import os
from unittest import result
import tqdm
import random
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
    year_str = byline.split("입력 : ")[-1].split(". ")[0]
    if int(year_str) < 2018:
        return True
    else:
        return False

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
        try:
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
        except:
            pass

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
    page_num = 1

    scrape_result = pd.DataFrame(
        columns=["titles", "urls", "summaries", "bylines_0", "bylines_1", "articlies"]
        )
    
    while True:
        result_df, is_done = get_article_list(page_num)
        scrape_result = pd.concat([scrape_result, result_df], ignore_index=True)
        page_num+=1
        if is_done:
            break

        print(f"{page_num} 스크랩 완료")
    
    scrape_result.to_csv(os.path.join("result", "hallailbo_opinions.csv"), encoding="utf-8-sig")