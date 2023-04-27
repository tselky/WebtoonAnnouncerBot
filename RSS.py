import sqlite3
import feedparser
import pandas as pd
import config

con = sqlite3.connect('test.db')
cur = con.cursor()


link = "https://www.webtoons.com/en/supernatural/eros-conquers-all/rss?title_no=3312"

data = {
    "episode_name": [], "date": [], "episode_link": [], 'episode_number': [], 'series_link': [], "announcement_check": [],
}
col_list = ["episode_name", "date", "episode_link", 'series_link', 'episode_number', "announcement_check"]


def set_series():
    sql = ''' UPDATE servers SET series = ?'''
    cur.execute(sql, link)
    rss_populate(link)
    con.commit()


def set_announce(channel):
    sql = ''' UPDATE servers SET ann_channel = ?'''
    cur.execute(sql, channel)
    con.commit()


def set_discussion(channel):
    sql = ''' UPDATE servers SET thr_channel = ?'''
    cur.execute(sql, channel)
    con.commit()


def append_data(arr: dict):
    try:
        for key, val in arr.items():
            data[key].append(val)
    except Exception as e:
        print("Append Data failed: ", e)


def retrieve_settings():
    sql = """SELECT series, ann_channel, thr_channel, ann_toggle, thread_toggle FROM servers"""
    cur.execute(sql)
    server = cur.fetchone()
    return server


# Backfills Pre-released Episodes
def rss_populate(link):
    feed = feedparser.parse(link)
    for entry in feed.entries:
        article_link = entry.link
        article_pubdate = entry.published
        # article_published_at = entry.published  # Unicode string
        # article_published_at_parsed = entry.published_parsed  # Time object
        # article_author = entry.author
        # content = entry.summary

        episode_data = {
            "episode_name": entry.title,
            "date": article_pubdate,
            "episode_link": article_link,
            "series_link": link,
            "episode_number": article_link.split('episode_no=', 1)[1]
        }

        append_data(episode_data)

    df1 = pd.DataFrame.from_dict(data, orient="index").T
    print(df1)

    try:
        print("TRY BLOCK rss_populate")
        df1.to_sql('episodes', con, if_exists='replace', index=False)


    except:
        print("EXCEPT BLOCK rss_populate")

# Returns dataframe of episode data to announce
def rss_post():
    sql = """SELECT series FROM servers"""
    cur.execute(sql)
    link = cur.fetchone()

    feed = feedparser.parse(link)
    for entry in feed.entries:
        article_link = entry.link
        article_pubdate = entry.published

        episode_data = {
            "episode_name": entry.title,
            "date": article_pubdate,
            "episode_link": article_link,
            "series_link": link,
            "episode_number": article_link.split('episode_no=', 1)[1]
        }

        append_data(episode_data)

    df1 = pd.DataFrame.from_dict(data, orient="index").T
    print(df1)

    try:
        print("TRY BLOCK")
        df1.to_sql('episodes', con, if_exists='replace', index=False)
        df2 = pd.read_sql("SELECT episode_name, date, episode_link, episode_number FROM episodes WHERE "
                          "announcement_check is NULL = ",  con)

    except:
        print("EXCEPT BLOCK rss_post")


# useless / vestigial
def announce():
    bd = pd.read_sql("SELECT episode_name, date, episode_link FROM episodes", con)  # fix
    re = bd[bd['announcement_check'].isna()]
    config.updateList.clear()
    for index, row in re.iterrows():
        config.updateList.append(
            (row['episode_name'], row['date'], row["episode_link"], row['ann_check']))
    config.updateList.reverse()
    print(config.updateList)
    print(len(config.updateList))


# useless / redundant
def checkToggle(str):
    ct = pd.read_sql("SELECT episode_name, date, episode_link FROM episodes", con)
    ct.loc[ct["episode_link"] == str, "announcement_check"] = 'yes'
    ct.to_sql("episodes", con, if_exists='append', index=False)


rss_populate(link)

