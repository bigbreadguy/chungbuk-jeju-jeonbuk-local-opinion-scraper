import os
import time
import tqdm
import requests
from bs4 import BeautifulSoup
import pandas as pd

def get_response(url:str):
    return requests.get(url)

def get_article_list(page_num:int):
    url_base = f"https://cdn.jemin.com/news/articleList.html?page={page_num}&total=12590&box_idxno=&sc_sub_section_code=S2N45&view_type=sm"
    while True:
        response = get_response(url_base)
        if not response.content == b"":
            break
        
        time.sleep(10)

    soup = BeautifulSoup(response.content, "html.parser", from_encoding="utf-8")
    section_list = soup.find(id="section-list")
    sections = section_list.find_all("li")

    return sections

def get_article_text(title):
    article_url = "https://cdn.jemin.com" + title.find("a").get("href")
    article_response = get_response(article_url)
    article = BeautifulSoup(article_response.content, "html.parser", from_encoding="utf-8")
    article_view = article.find(id="article-view-content-div")
    paragraphs = article_view.find_all("p")
    article_text = "\n".join([p.get_text() for p in paragraphs])

    return article_text

def get_articles(sections):
    titles = []
    previews = []
    articles = []
    bylines_0 = []
    bylines_1 = []
    bylines_2 = []

    for section in sections:
        title = section.find(class_="titles")
        title_text = title.get_text()

        paragraph_preview = section.find(class_="lead line-6x2").find("a")
        preview_text = paragraph_preview.get_text()
        
        article_text = get_article_text(title)

        byline = section.find(class_="byline").find_all("em")
        byline_text_0 = byline[0].get_text()
        byline_text_1 = byline[1].get_text()
        byline_text_2 = byline[2].get_text()

        titles.append(title_text)
        previews.append(preview_text)
        articles.append(article_text)
        bylines_0.append(byline_text_0)
        bylines_1.append(byline_text_1)
        bylines_2.append(byline_text_2)
    
    articles_frame = pd.DataFrame({
        "titles": titles,
        "previews": previews,
        "articles": articles,
        "bylines_0": bylines_0,
        "bylines_1": bylines_1,
        "bylines_2": bylines_2,
    })

    return articles_frame

#if __name__=="__main__":