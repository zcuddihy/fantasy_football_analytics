#%%
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import secrets
import numpy as np
import database as db
import time

# Install driver
opts = webdriver.ChromeOptions()
opts.headless = True

driver = webdriver.Chrome(ChromeDriverManager().install(), options=opts)


def site_login():
    LOGIN_URL = "https://stathead.com/users/login.cgi/login"
    payload = {
        "username": secrets.username,
        "password": secrets.password,
    }
    driver.get(LOGIN_URL)
    driver.find_element_by_id("username").send_keys(payload["username"])
    driver.find_element_by_id("password").send_keys(payload["password"])
    driver.find_element_by_id("sh-login-button").click()


site_login()

# %%
def get_rushing_stats(url: str):
    driver.get(url)

    # Get table from URL
    soup = BeautifulSoup(driver.page_source, "lxml")
    soup_table = soup.find("table", {"id": "results"})
    df = pd.read_html(str(soup_table))[0].droplevel(0, axis=1)

    # Clean table and adjust data before inserting to database
    df.drop(columns=["Rk", "Lg", "G#", "Y/A"], inplace=True)
    df.rename(
        columns={
            "Player": "player",
            "Pos": "position",
            "Age": "age",
            "Date": "game_date",
            "Tm": "team",
            "Unnamed: 7_level_1": "home_or_away",
            "Opp": "opponent",
            "Result": "game_result",
            "Week": "week",
            "Day": "day_of_week",
            "Att": "rushing_attempts",
            "Yds": "rushing_yards",
            "TD": "rushing_TD",
        },
        inplace=True,
    )

    # Remove the asterisk from the player names
    df.player = df.player.str.strip("*")

    # Remove sub headers within table
    df = df[df.player != "Player"]

    # Clean the position column
    df.position = np.where(df.position == "HB", "RB", df.position)
    df.position = df.position.str.strip("'")

    # Convert the age column decimal
    # Current format is years-days
    df.age = (
        df.age.str.split("-").str[0].astype(float)
        + df.age.str.split("-").str[1].astype(float) / 365
    )
    df.age = round(df.age, 3)

    # Add home or away
    df.home_or_away = np.where(df.home_or_away == "@", "away", "home")

    # Clean the game result into two columns
    df["game_score"] = df.game_result.str.split(" ").str[1]
    df.game_result = df.game_result.str.split(" ").str[0]

    # Add season to data
    df["season"] = np.where(
        df.game_date.str.split("-").str[1].astype(int) == 1,
        df.game_date.str.split("-").str[0].astype(int) - 1,
        df.game_date.str.split("-").str[0].astype(int),
    )
    return df


# %%


def scrape_data():

    # Create a connection to the SQLite database
    conn = db.create_connection("../data/football_stats.db")
    db.create_tables(conn)

    # Scrape the rushing data
    for week in range(1, 19, 1):
        offset = 0
        while True:
            # Limit request rate
            time.sleep(1.1)
            # Scrape the URL
            RUSH_URL = f"https://stathead.com/football/pgl_finder.cgi?request=1&game_num_max=99&week_num_max={week}&order_by=rush_att&match=game&season_start=1&year_max=2021&order_by_asc=0&season_end=-1&week_num_min={week}&age_min=0&game_type=R&age_max=99&positions[]=qb&positions[]=rb&positions[]=wr&positions[]=te&game_num_min=0&year_min=1972&cstat[1]=rush_att&ccomp[1]=gt&cval[1]=1&offset={offset}"
            try:
                df = get_rushing_stats(RUSH_URL)
            except:
                df = None
            # Check if a table wasn't found which indicates end of the scraping for the given week
            if df is None:
                break
            # Save the data
            df.to_sql("rushing", con=conn, if_exists="append", index=False)
            print(f"Week: {week}, offset: {offset}")
            # Increase the offset for the URL
            offset += 100

    conn.close()


scrape_data()


# %%

