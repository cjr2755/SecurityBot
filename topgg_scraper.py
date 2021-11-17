from bot_class import Bot
from bs4 import BeautifulSoup
from random import randint
from requests import get
from selenium import webdriver
from time import sleep
from urllib.parse import unquote


def search_website(bot_name:str, bot:Bot) -> str:
    """
    Search topgg.com to see if there is a match.
    If there is a match, pass the result to the website parsing method.
    """
    website = "https://top.gg"
    bot_name=bot_name.replace("-", " ").lower()
    found = False
    search_string = website+"/search?q="+bot_name
    # Make the string work if the bot name has spaces in it
    search_string = search_string.replace(" ", "%20")
    # data = requests.get(search_string)
    # html = data.text

    driver = webdriver.Firefox()
    driver.get(search_string)
    sleep(3+randint(0,3))
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    driver.close()

    results = soup.find_all(class_="base__AnimatedFlex-sc-1f9zlm1-3 fexVvd EntityList__BorderRadius-sc-1r6e39u-0 cNavCI")[0].contents
    for result in results:
        # The Classes change sometimes, so this must be done :(
        result_name = result.next.next.contents[1].next.next.next.text
        result_link = result.next.next.contents[0].contents[0].attrs['href']

        if result_name.lower() == bot_name.lower():
            found = True
            return scrape_discord_bot_list(website, result_link, bot)      
        
    if not found:
        return f"Error, bot could not be found on {website}"


def scrape_perms(url) -> int:
    driver = webdriver.Firefox()
    driver.get(url)
    sleep(10+randint(0,5))

    

    try:
        return int(unquote(driver.current_url).split("permissions")[-1].split("&")[0].strip("="))
    except ValueError as e:
        return None
    finally:
        driver.close()
    

def scrape_discord_bot_list(website:str, result_link:str, bot:Bot) -> int:
    """"
    Go through the resulting website and pulls relevant information of
    off the website.
    """
    bot_review_score = 0
    bot_server_count = 0
    bot_user_count = 0

    url = website + result_link
    data = get(url)
    html = data.text
    soup = BeautifulSoup(html, 'html.parser')
    

    try:
        # result = soup.find_all(class_="col-12 col-md-6 bot-info")[0].text.split("\n")
        bot_review_score = soup.find_all(class_="chakra-text css-o3nsz6")[0].text
        bot_review_count = soup.find_all(class_="chakra-text css-o3nsz6")[1].text
    except:
        bot.warnings.append(f"Could not find review information from {url}")
        bot_review_score = 0
        bot_review_count = 0

    bot_image = soup.find_all(class_="chakra-image css-ay5wn")[0].attrs['src']

    bot_invite = website + soup.find_all(class_="chakra-link chakra-button css-1wmxbjx")[0].attrs['href']
    # for invite in invite_data:
    #     if type(invite) != str and "Add" in invite.text: 
    #         bot_invite = invite.contents[0].attrs['href']
    #         break 

    
    for result in soup.find_all(class_="chakra-stack css-76k36x"):
        if result.contents[0].text == "Server Count":
            print(result.text)
            bot_server_count = result.contents[1].text
            break

    bot_prefix = soup.find_all(class_="chakra-text css-mewo4z")[0].text.split(" ",1)[0]

    if bot_server_count == "unknown":
        bot_server_count = 0
    
    try:
        bot_website = soup.find_all(class_="chakra-link css-1avq5i6")[0].find_all(class_="chakra-text css-1bvyf9q")[0].text
    except Exception as e:
        bot.warnings.append(f"Could not find website for {website+result_link}")
        bot_website = ""

    # for result in soup.find_all("a", target="_blank"):
    #     if result.text.strip("\n") == "Website":
    #         bot_website = result.attrs['href']

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