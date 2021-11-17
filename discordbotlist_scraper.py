from bot_class import Bot
from bs4 import BeautifulSoup
from requests import get
from selenium import webdriver


def search_website(bot_name:str, bot:Bot) -> str:
    """
    Search discordbotlist.com to see if there is a match.
    If there is a match, pass the result to the website parsing method.
    """
    website = "https://discordbotlist.com"
    bot_name=bot_name.replace("-", " ").lower()
    found = False
    search_string = website+"/search?q="+bot_name
    # Make the string work if the bot name has spaces in it
    search_string = search_string.replace(" ", "%20")
    # data = requests.get(search_string)
    # html = data.text

    driver = webdriver.Firefox()
    driver.get(search_string)

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.close()

    results = soup.find_all(class_="col-12 col-md-3") 
    for result in results:
        result_name = result.find_all(class_="bot-name")[0].next.next
        result_link = result.find_all("a", href=True)[0]['href']
        if result_name.lower() == bot_name:
            found = True
            return scrape_discord_bot_list("https://discordbotlist.com"+result_link, bot)
    if not found:
        return f"Error, bot could not be found on {website}"


def scrape_perms(url) -> int:
    results = get(url)
    try:
        perm_num = int(results.url.split("permissions")[-1].split("&")[0].strip("="))
        return perm_num
    except ValueError as e:
        return None


def scrape_discord_bot_list(url:str, bot:Bot) -> int:
    """"
    Go through the resulting website and pulls relevant information of
    off the website.
    """
    data = get(url)
    html = data.text
    soup = BeautifulSoup(html, 'html.parser')

    try:
        result = soup.find_all(class_="col-12 col-md-6 bot-info")[0].text.split("\n")
        bot_review_score = result[4].split(" ")[1]
        bot_review_count = result[4].split(" ")[3]
    except:
        bot.warnings.append(f"Could not find review information from {url}")
        bot_review_score = 0
        bot_review_count = 0

    bot_image = soup.find_all(class_="col-12 col-md-2")[0].contents[0].attrs['src']

    invite_data = soup.find_all(class_="col-12 col-md-6 bot-info")[0].contents
    for invite in invite_data:
        if type(invite) != str and "Add" in invite.text: 
            bot_invite = invite.contents[0].attrs['href']
            break 

    data = soup.find_all(class_="col-12 col-md-4")[0].contents[2].text.split(" ")
    for count,item in enumerate(data):
        if item == "Servers:":
            bot_server_count = data[count+1]
        elif item == "Users:":
            bot_user_count = data[count+1]
        elif item == "Prefix:":
            bot_prefix = data[count+1]
        count += 1
    if bot_server_count == "unknown":
        bot_server_count = 0
    if bot_user_count == "unknown":
        bot_user_count = 0
    
    for result in soup.find_all("a", target="_blank"):
        if result.text.strip("\n") == "Website":
            bot_website = result.attrs['href']

    # Pull the permission number from the invite link. 
    bot_permission_score = scrape_perms(bot_invite)

    # Check for error
    if bot_permission_score is None:
        return None

    # Add the discovered data to the bot
    if bot_server_count != 0:
        bot.server_count.append(bot_server_count)
    if bot_user_count != 0:
        bot.user_count.append(bot_user_count)
    
    # Scale up to a score out of 100 
    bot.review_score.append(float(bot_review_score)*20)
    bot.review_count.append(bot_review_count)
    
    bot.image = bot_image
    bot.prefix=bot_prefix
    bot.website=bot_website
    bot.load_permissions(bot_permission_score, bot.get_permission_dict())
    
    return ""