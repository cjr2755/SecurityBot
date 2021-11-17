from selenium.webdriver.firefox.webdriver import WebDriver
from urllib.parse import unquote
from bot_class import Bot
from bs4 import BeautifulSoup
from random import randint
from requests import get
from selenium import webdriver
from time import sleep


def search_website(bot_name:str, bot:Bot) -> int:
    """
    Search botsondiscord.com to see if there is a match.
    If there is a match, pass the result to the website parsing method.
    """
    website = "https://bots.ondiscord.xyz"
    
    found = False
    search_string = website+"/search?query="+bot_name
    
    driver = webdriver.Firefox()
    driver.get(search_string)

    # Click on the Accept Button to view results (if it exists)
    try:
        sleep(3+randint(0,3))
        button = driver.find_element_by_class_name("css-1litn2c")
        sleep(1+randint(0,3))
        button.click()
    except Exception as e:
        pass 

    sleep(3+randint(0,3))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # I don't know why this part has to be different from the rest, but it is what it is. 
    results = soup.body.find("div", {"class":"bot-list"}).contents
    
    for result in results:
        result_name = result.find_all(class_="bc-header")[0].text
        result_link = result.find_all(class_="button is-primary")[0].attrs['href']
        if result_name.lower() == bot_name.lower():
            found = True
            result = scrape_discord_bot_list("https://bots.ondiscord.xyz"+result_link, bot, driver)
            return result
    if not found:
        return None


def scrape_perms(url) -> int:
    results = get(url)
    try:
        perm_num = int(results.url.split("permissions")[-1].split("&")[0].strip("="))
        return perm_num
    except ValueError as e:
        return None


def scrape_discord_bot_list(url:str, bot:Bot, driver:WebDriver) -> int:
    """"
    Go through the resulting website and pulls relevant information of
    off the website.
    """
    bot_review_score = 0
    bot_server_count = 0

    driver.get(url)

    # Click on the Accept Button to view results
    sleep(3+randint(0,3))
    try:
        button = driver.find_element_by_class_name("css-1litn2c")
        sleep(1+randint(0,3))
        button.click()
    except Exception as e:
        pass
    
    sleep(3+randint(0,3))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    try:
        # Gather Bot Invite Information
        invite_info = soup.find_all(class_="stats")[0].contents
        for result in invite_info:
            if "invites total" in result.text:
                bot_server_count = int(result.text.split()[0].replace(",",""))
                break
        
        # Gather Bot Image
        bot_image = soup.find_all(class_="avatar-wrapper")[0].contents[0].attrs['src']

        # Gather Bot Review Information
        bot_review_info = soup.find_all(class_="positive")
        for result in bot_review_info:
            if 'style' in result.attrs:
                # Pull out the review score and round it down to two places 
                bot_review_score = round(float(result.attrs['style'].split(":")[-1].strip("%;")),2)
                break

        # Gather Bot Prefix
        bot_prefix_info = soup.find_all(class_="general-info")[0].contents
        for result in bot_prefix_info:
            if "Prefix" in result.text:
                bot_prefix = result.text.split(" ")[-1] 
                break

        # Gather Bot Website Information
        bot_website_info = soup.find_all(class_="button is-light")
        for result in bot_website_info:
            if "Website" in result.text:
                bot_website = result.attrs['href']
                break
        
        # Gather invite link information
        #
        # Find & click on the invite button 
        #    - this opens up a second tab
        invite_button = driver.find_elements_by_link_text("Add to Server")[0]
        invite_button.click()
        # Switch to new window
        #   - driver.window_handles contains a list of open tabs 
        sleep(5+randint(0,3))
        driver.switch_to.window(driver.window_handles[-1])

        # Pull the current URL (which contains the permission number)
        # use urllib to remove percent encoding
        url_without_percents = unquote(driver.current_url)
        bot_perm_info = url_without_percents.split("&")

        # Search for permission in URL
        for data in bot_perm_info:
            if 'permission' in data:
                bot_permission_score = int(data.split("=")[-1])
                break

    except:
        pass


    # Add the discovered data to the bot
    if bot_server_count != 0:
        bot.server_count.append(bot_server_count)

    bot.review_score.append(float(bot_review_score))

    bot.image = bot_image
    bot.prefix=bot_prefix
    bot.website=bot_website
    
    # Only load up the bot if the permissions are not alredy done.
    bot.load_permissions(bot_permission_score, bot.get_permission_dict())
    
    # Close second tab
    driver.close()
    # Switch back to first tab
    driver.switch_to.window(driver.window_handles[-1])
    # Close first tab
    driver.close()

    return ""

if __name__ == "__main__":
    steven = Bot()
    search_website("Dyno", steven)