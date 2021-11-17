import requests
from bot_class import Bot
import discordbotlist_scraper
import botsondiscord_scraper
import topgg_scraper

NUMBER_OF_WEBSITES = 3

def search_websites(bot_name:str, bot:Bot):
    errors = 0
    outputs = []
    outputs.append(topgg_scraper.search_website(bot_name, bot))
    outputs.append(discordbotlist_scraper.search_website(bot_name, bot))
    
    outputs.append(botsondiscord_scraper.search_website(bot_name, bot))
    

    for output in outputs:
        if output != "":
            errors += 1
            # The output will be 'Error, bot could not be found on <website name>'
            bot.warnings.append(output)

    if errors >= NUMBER_OF_WEBSITES:
        bot.error = "Could not find the bot on any websites!"
    



if __name__ == "__main__":
    stanley = Bot()
    search_websites("Dyno",stanley)
    stanley.calculate_score()
    print("he-man")