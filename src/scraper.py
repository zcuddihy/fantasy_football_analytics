#%%
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import secrets
import numpy as np

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

import numpy as np


def get_rushing_stats():
    RUSH_URL = "https://stathead.com/football/pgl_finder.cgi?request=1&game_num_max=99&week_num_max=7&order_by=rush_att&match=game&season_start=1&year_max=2021&order_by_asc=0&season_end=-1&age_min=0&week_num_min=7&game_type=R&age_max=99&game_num_min=0&year_min=1972&cstat[1]=rush_att&ccomp[1]=gt&cval[1]=1&offset=5700"
    driver.get(RUSH_URL)

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
            "Day": "day",
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


df = get_rushing_stats()

df

# %%


def scrape_data():
    RUSH_URL = "https://stathead.com/football/pgl_finder.cgi?request=1&game_num_max=99&week_num_max=7&order_by=rush_att&match=game&season_start=1&year_max=2021&order_by_asc=0&season_end=-1&age_min=0&week_num_min=7&game_type=R&age_max=99&game_num_min=0&year_min=1972&cstat[1]=rush_att&ccomp[1]=gt&cval[1]=1&offset=5700"
