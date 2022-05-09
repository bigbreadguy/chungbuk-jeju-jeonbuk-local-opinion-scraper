import os
import datetime
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_response(url:str):
    response = requests.get(url)

    return response

def get_article_paragraphs(url:str):
    response = get_response(url)
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")

    paragraphs = soup.find(id="articleBody").get_text().replace("< 저작권자 © 제주신문 무단전재 및 재배포금지 >", "")

    return paragraphs


def get_article_list(page_num:int):
    url_base = f"http://www.jejupress.co.kr/news/articleList.html?page={page_num}&total=3769&sc_section_code=&sc_sub_section_code=S2N65&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&sc_word2=&sc_andor=&sc_order_by=E&view_type="
    response = get_response(url_base)
    
    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    table_view = soup.find(id="viewFINE").find("table")
    table_body = table_view.find("tr").find("td").find_all("table")[5]\
        .find("tr").find("td").find("table")\
            .find("tr").find("td").find("table")
    table_rows = table_body.find_all("tr")

    is_done = False
    titles = []
    urls = []
    bylines_0 = []
    bylines_1 = []
    articles = []
    for tr in table_rows:
        title_object = tr.find(class_="ArtList_Title")
        table_descriptions = tr.find_all("td")
        if not title_object is None:
            title = title_object.find("a").get_text()
            url = "http://www.jejupress.co.kr/news/" + title_object.find("a").get("href")
            
            td_texts = []
            for td in table_descriptions:
                td_texts.append(td.get_text())
            
            byline_0 = td_texts[-2]
            byline_1 = td_texts[-1]

            date = datetime.datetime.strptime(byline_1, "%Y-%m-%d")
            if date < datetime.datetime(2018, 5, 1):
                is_done = True
                break

            article = get_article_paragraphs(url)

            titles.append(title)
            urls.append(url)
            bylines_0.append(byline_0)
            bylines_1.append(byline_1)
            articles.append(article)
    
    result_df = pd.DataFrame(
        {
            "titles": titles,
            "urls": urls,
            "bylines_0": bylines_0,
            "bylines_1": bylines_1,
            "articles": articles,
        }
    )

    return result_df, is_done

if __name__=="__main__":
    if not os.path.exists("./result"):
        os.makedirs("./result")

    result_dir = os.path.join("./result", "jejusinmun")
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    
    page_num = 1

    while True:
        result_df, is_done = get_article_list(page_num)
        result_df.to_csv(os.path.join(result_dir, f"jejusinmun_opinions_p{page_num}.csv"), encoding="utf-8-sig")
        print(f"{page_num} 페이지 스크랩 완료")

        if is_done:
            break

        page_num+=1