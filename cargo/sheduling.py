import schedule
import time


def send_discord_message(match):
    print("Discord message: " + str(match))


schedule.every().day.at("11:39:30").do(send_discord_message, match="Hey")

while True:
    schedule.run_pending()
    time.sleep(1)
