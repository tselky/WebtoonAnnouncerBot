########################################################################################################################

# This file contains functions related to direct modification the sqlite database for the discord
# bot and RSS data handling As this bot originally was more personalized and used CSV files, I'm currently publicly
# reworking it for general use and upgrading it to be a bit cleaner and use sqlite.

# tselky#9999 @discord

########################################################################################################################
import sqlite3
import feedparser
import pandas as pd
import config

con = sqlite3.connect('test.db')
cur = con.cursor()
link = ""  # Webtoons series RSS link
data = {
    "episode_name": [], "date": [], "episode_link": [], 'episode_number': [], 'series_link': [],
    "announcement_check": [],
}
col_list = ["episode_name", "date", "episode_link", 'series_link', 'episode_number', "announcement_check"]


# Sets the series in database
def set_series():
    sql = ''' UPDATE servers SET series = ?'''
    cur.execute(sql, link)
    rss_populate(link)
    con.commit()


# Sets the announcement channel in the database (channel id)
def set_announce(channel):
    sql = ''' UPDATE servers SET ann_channel = ?'''
    cur.execute(sql, channel)
    con.commit()


# Sets the thread channel in the database (channel id)
def set_discussion(channel):
    sql = ''' UPDATE servers SET thr_channel = ?'''
    cur.execute(sql, channel)
    con.commit()


# Function to append data values to specified keys based on key value pairs.
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


# Backfills Pre-released Episodes by retrieving RSS data from the RSS link and processing it into the episode_data dictionary
# This function is intended for use in the setup.py file or experienced manual use.
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

    # Dataframe 1 (df1) is set to the data from the dictionary and is ordered by index
    df1 = pd.DataFrame.from_dict(data, orient="index").T
    # print(df1)

    # Tries to populate the database with the dataframe data in the episodes table.
    try:
        print("TRY BLOCK rss_populate")
        df1.to_sql('episodes', con, if_exists='replace', index=False)
    except:
        print("EXCEPT BLOCK rss_populate")

# Returns dataframe of episode data to announce
def rss_update():
    # Retrieve the RSS feed
    feed = feedparser.parse(link)

    # Create a DataFrame from the feed data
    episode_data = []
    for entry in feed.entries:
        article_link = entry.link
        article_pubdate = entry.published

        episode_data.append({
            "episode_name": entry.title,
            "date": article_pubdate,
            "episode_link": article_link,
            "series_link": link,
            "episode_number": article_link.split('episode_no=', 1)[1],
            "announcement_check": None
        })
    df = pd.DataFrame.from_dict(episode_data)

    # Query the database to check for existing episodes
    existing_episodes = pd.read_sql_query(f"SELECT episode_link FROM episodes WHERE series_link='{link}'", con)

    # Filter out existing episodes from the DataFrame
    new_episodes = df[~df['episode_link'].isin(existing_episodes['episode_link'])]

    # Update the database with the new data
    try:
        new_episodes.to_sql('episodes', con, if_exists='append', index=False)
    except Exception as e:
        print(f"Error updating database: {e}")





# USELESS / VESTIGIAL UNTIL REWORK IS DONE
# Originally this function would be called by the main webtoons loop after a post had been successfully been made
# The function would check the announcement_check column in the database to exclude the episode from being announced again.
def checkToggle(ep_link):
    # Construct SQL query
    sqlite_statement = "SELECT episode_name, date, episode_link, announcement_check FROM episodes WHERE episode_link = ?"

    # Query database and update dataframe
    ct = pd.read_sql(sqlite_statement, con, params=(ep_link,))
    print(ct)
    if not ct.empty:
        announcement_check = ct.iloc[0]["announcement_check"]
        if announcement_check is None:
            ct.loc[ct["episode_link"] == ep_link, "announcement_check"] = 'yes'
            ct.to_sql("episodes", con, if_exists='update', index=False)
            con.commit() # Commit changes to database
        else:
            print("Episode has already been announced.")
    else:
        print("No matching episodes found in the database.")





# USELESS / VESTIGIAL UNTIL REWORK IS DONE
# Originally this function would read some episode data and check if a toggle column had been filled to determine if
# an episode had been announced or not. If not, it would add the data then reverse the list.
# The list is reversed because the episodes are inserted in a backwards order due to appending the rows top to bottom.
# The update list is used by the main webtoons announcement loop in Bot.py to make posts and threads.
def announce():
    print("ANNOUNCE")
    # Select only episodes that haven't been announced
    sql = "SELECT episode_name, date, episode_link, episode_number FROM episodes WHERE announcement_check IS NULL"
    bd = pd.read_sql(sql, con, params=())
    announce_list = []
    for index, row in bd.iterrows():
        announce_list.append((row['episode_name'], row['date'], row["episode_link"], row["episode_number"]))
        # Update announcement_check field in database
        update_sql = "UPDATE episodes SET announcement_check = 'yes' WHERE episode_link LIKE ?"
        con.execute(update_sql, (f'%{row["episode_link"]}',))
        con.commit()  # Commit changes to database

    announce_list.reverse()
    print(announce_list)
    if not announce_list:
        print("No new episodes to announce.")
    return announce_list


