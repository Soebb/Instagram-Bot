import os, pickle
from instaloader import Instaloader, ConnectionException
from dotenv import load_dotenv
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
import geckodriver_autoinstaller
from glob import glob
from os.path import expanduser
from sqlite3 import OperationalError, connect
from collections.abc import Sequence
from contextlib import closing
from typing import Any, Mapping
import sqlite3

load_dotenv()

SQL_STATEMENT_CREATE_TABLE = r"""
CREATE TABLE
moz_cookies (
    id INTEGER PRIMARY KEY,
    originAttributes TEXT NOT NULL DEFAULT '',
    name TEXT,
    value TEXT,
    host TEXT,
    path TEXT,
    expiry INTEGER,
    lastAccessed INTEGER,
    creationTime INTEGER,
    isSecure INTEGER,
    isHttpOnly INTEGER,
    inBrowserElement INTEGER DEFAULT 0,
    sameSite INTEGER DEFAULT 0,
    rawSameSite INTEGER DEFAULT 0,
    schemeMap INTEGER DEFAULT 0,
    CONSTRAINT moz_uniqueid UNIQUE (name, host, path, originAttributes)
)
"""

SQL_STATEMENT_INSERT_COOKIE = r"""
INSERT INTO
  moz_cookies (
    name,
    value,
    host,
    path,
    expiry,
    lastAccessed,
    creationTime,
    isSecure,
    isHttpOnly
  )
VALUES (
    :name,
    :value,
    :domain,
    :path,
    :expiry,
    :access_time,
    :creation_time,
    :secure,
    :httponly
  );
"""

def generate_cookies_db(
    cookies: Sequence[Mapping[str, Any]],
    access_time: int,
    creation_time: int,
    db_path: str | os.PathLike,
) -> None:
    with closing(sqlite3.connect(db_path)) as connection:
        with closing(connection.cursor()) as cursor:
            cursor.execute(SQL_STATEMENT_CREATE_TABLE)
            for cookie in cookies:
                values = {
                    "access_time": access_time,
                    "creation_time": creation_time,
                    "domain": cookie.get("domain"),
                    "expiry": cookie.get("expiry"),
                    "httponly": cookie.get("httpOnly", False),
                    "name": cookie["name"],
                    "path": cookie.get("path"),
                    "secure": cookie.get("secure", False),
                    "value": cookie["value"],
                }
                cursor.execute(SQL_STATEMENT_INSERT_COOKIE, values)
            return cursor
        #connection.commit()


def get_cookiefile(path):
    cookiefiles = glob(expanduser(path))
    if not cookiefiles:
        raise SystemExit("No Firefox cookies.sqlite file found. Use -c COOKIEFILE.")
    print("cookiefiles : ")
    print(cookiefiles)
    return cookiefiles[0]


def import_session(cookie_data, sessionfile):
    """
    print("Using cookies from {}.".format(cookiefile))
    conn = connect(f"file:{cookiefile}?immutable=1", uri=True)
    try:
        cookie_data = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE baseDomain='instagram.com'"
        )
    except OperationalError:
        cookie_data = conn.execute(
            "SELECT name, value FROM moz_cookies WHERE host LIKE '%instagram.com'"
        )
    """
    instaloader = Instaloader(max_connection_attempts=1)
    instaloader.context._session.cookies.update(cookie_data)
    username = instaloader.test_login()
    if not username:
        raise SystemExit("Not logged in. Are you logged in successfully in Firefox?")
    print("Imported session cookie for {}.".format(username))
    instaloader.context.username = username
    instaloader.save_session_to_file(sessionfile)
    return instaloader


geckodriver_autoinstaller.install() # if it doesn't exist, download it automatically,

option = Options()
option.binary_location = "/opt/firefox/firefox"    #chrome binary location specified here
option.add_argument("--no-sandbox") #bypass OS security model
option.add_argument("--headless")

driver = webdriver.Firefox(options=option)

driver.get("https://www.instagram.com/")

username = WebDriverWait(driver, timeout=60).until(
    lambda d: d.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input'))
USER = os.environ.get("INSTAGRAM_USERNAME", "")
username.send_keys(USER)

password = driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[2]/div/label/input')
PASSWORD = os.environ.get("PASSWORD", "")
password.send_keys(PASSWORD)

enter = driver.find_element(By.XPATH, '//*[@id="loginForm"]/div/div[3]/button')
enter.click()

out_cook = "cook.pkl"
pickle.dump(driver.get_cookies(), open(out_cook, "wb"))
outpath = "./cook.sqlite"

cookies = pickle.load(open(out_cook, "rb"))
access_time_us = int(os.path.getmtime(out_cook) * 1_000_000)
creation_time_us = int(os.path.getctime(out_cook) * 1_000_000)
data = generate_cookies_db(cookies, access_time_us, creation_time_us, outpath)

driver.quit()
insta = import_session(data, USER)


class Config:
    API_ID = int(os.environ.get("API_ID", ""))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
    USER = os.environ.get("INSTAGRAM_USERNAME", "")
    PASSWORD = os.environ.get("PASSWORD", "")
    OWNER = os.environ.get("OWNER_ID", "")
    INSTA_SESSIONFILE_ID = os.environ.get("INSTA_SESSIONFILE_ID", None)
    S = "0"
    STATUS = set(int(x) for x in (S).split())
    L=insta
    HELP="""
You can Download almost anything From your Instagram Account.

<b>What Can Be Downloaded?:</b>

1. All posts of any Profile. (Both Public and Private,for private profiles you need to be a follower.)
2. All Posts from your feed.
3. Stories of any profile (Both Public and Private,for private profiles you need to be a follower.)
4. DP of any profile (No need to follow)
5. Followers and Followees List of any Profile.
6. List of followees who follows back the given username.
7. List of followees who are not following back the given username.
8. Stories of your Followees.
9. Tagged posts of any profile.
10. Your saved Posts.
11. IGTV videos.
12. Highlights from any profiles.
13. Any Public Post from Link(Post/Reels/IGTV)


<b>How to Download:</b>

Its Easy!!
You Need to login into your account by /login. 

You have two Options:

1. From Username:

Just send any instagram username.

For Example:
<code>samantharuthprabhuoffl</code>
<code>subin_p_s_</code>
<code>_chill_manh_7</code>


2. From URL:

You can also sent a post link to download the post or video.

For Example:
<code>https://www.instagram.com/p/CL4QbUiLRNW/?utm_medium=copy_link</code>
<code>https://www.instagram.com/taylorswift/p/CWds7zapgHn/?utm_medium=copy_link</code>


<b>Available Commands and Usage</b>

/start - Check wheather bot alive.
/restart - Restart the bot (If you messed up anything use /restart.)
/help - Shows this menu.
/login - Login into your account.
/logout - Logout of your account.
/account - Shows the details of logged in account.

/posts <username> - Download posts of any username. Use /posts to download own posts or <code> /posts <username> </code>for others.
Example : <code>/posts samantharuthprabhuoffl</code>

/igtv <username> - Download IGTV videos from given username. If no username given, downloads your IGTV.

/feed <number of posts to download> - Downloads posts from your feed.If no number specified all posts from feed will be downloaded.
Example: <code>/feed 10</code> to download latest 10 posts from feed.

/saved <number of posts to download> - Downloads your saved posts. If no number specified all saved posts will be downloaded.
Example: <code>/saved 10</code> to download latest 10 saved posts.

/followers <username> - Get a list of all followers of given username. If no username given, then your list will be retrieved.
Example: <code>/followers samantharuthprabhuoffl</code>

/followees <username> - Get a list of all followees of given username. If no username given, then your list will be retrieved.

/fans <username> - Get a list of of followees who follow back the given username. If no username given, your list will be retrieved.

/notfollowing <username> - Get a list of followees who is not following back the given username.

/tagged <username> - Downloads all posts in which given username is tagged. If nothing given your tagged posts will be downloaded.

/story <username> - Downloads all stories from given username. If nothing given your stories will be downloaded.

/stories - Downloads all the stories of all your followees.

/highlights <username> - Downloads highlights from given username, If nothing given your highlights will be downloaded.


"""
    HOME_TEXT = """
<b>Helo, [{}](tg://user?id={})

This is a bot of [{}](www.instagram.com/{}) to manage his Instagram account. 
I can only work for my master [{}](tg://user?id={}).
But you can Deploy the same bot for your use from the below source code.

Use /help to know What I can Do?</b>
"""
    HOME_TEXT_OWNER = """
<b>Helo, [{}](tg://user?id={})
I am your assistant to manage your Instagram account.

Use /help to know what I can do for you.</b>
"""

