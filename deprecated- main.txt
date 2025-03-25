import bot
from dotenv import load_dotenv
import os

def configure():
    load_dotenv()

if __name__ == "__main__":
    configure()
    bot.run(os.getenv('token'))