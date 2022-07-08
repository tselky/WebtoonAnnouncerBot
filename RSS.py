import time
import feedparser
import webbrowser
import pandas as pd
import re
import config
import sqlite3

con = sqlite3.connect('test.db')
cur = con.cursor()

link = "https://www.webtoons.com/en/slice-of-life/pigminted/rss?title_no=482"

data = {
    "episode_name": [], "date": [], "episode_link": [], "announcement_check": [], 'series_link': []
}
col_list = ["episode_name", "date", "episode_link", "announcement_check", 'series_link']


def append_data(arr: dict):
    try:
        for key, val in arr.items():
            data[key].append(val)
    except Exception as e:
        print("Append Data failed: ", e)


def rectify_link():
    pass


def get_link():
    pass


def check_rss():
    feed = feedparser.parse(link)
    # feed_entries = feed.entries
    for entry in feed.entries:
        article_link = entry.link
        article_pubdate = entry.published
        article_published_at = entry.published  # Unicode string
        article_published_at_parsed = entry.published_parsed  # Time object
        article_author = entry.author
        content = entry.summary

        episode_data = {
            "episode_name": entry.title,
            "date": article_pubdate,
            "episode_link": article_link,
            "series_link": link
        }

        append_data(episode_data)

    df1 = pd.DataFrame.from_dict(data, orient="index").T

    try:
        print("TRY BLOCK")
        df2 = pd.read_sql(("SELECT episode_name, date, episode_link FROM episodes WHERE series_link = (?)", (link,)), con)

        merge = pd.concat([df1, df2]).drop_duplicates(subset=["episode_name", "date"],
                                                      keep='last').reset_index(drop=True)
        merge.to_sql('episodes', con, if_exists='append', index=False)
        pd.set_option('display.max_columns', None)

    except:
        print("EXCEPT BLOCK")
        df1.to_sql("episodes", con, if_exists='append', index=False)


def announce():
    bd = pd.read_sql(("SELECT episode_name, date, episode_link FROM episodes WHERE series_link = (?)", (link,)), con)
    re = bd[bd['announcement_check'].isna()]

    config.updateList.clear()
    for index, row in re.iterrows():
        config.updateList.append(
            (row['episode_name'], row['date'], row["episode_link"], row['announcement_check']))
    config.updateList.reverse()
    print(config.updateList)
    print(len(config.updateList))


def checkToggle(str):
    ct = pd.read_sql(("SELECT episode_name, date, episode_link FROM episodes WHERE series_link = (?)", (link,)), con)
    ct.loc[ct["episode_link"] == str, "announcement_check"] = 'yes'
    ct.to_sql("episodes", con, if_exists='append', index=False)


check_rss()
