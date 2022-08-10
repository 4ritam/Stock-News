import requests
from bs4 import BeautifulSoup
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
MESSAGE_SEND = False

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

stock_api = "https://www.alphavantage.co/query?"
stock_api_key = "K5PTN7OBV0OGX0JP"

stock_api_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_api_key,
    "outputsize": "compact"
}

negetive_value = False

with requests.get(stock_api, stock_api_parameters) as file:
    news_date = list(file.json()["Time Series (Daily)"].keys())[0]
    data = list(file.json()["Time Series (Daily)"].values())
    initial_value = float(data[1]['3. low'])
    new_value = float(data[0]['3. low'])
    changed_value = new_value - initial_value
    changed_value_percentage = int(changed_value / initial_value * 100)
    if changed_value_percentage < 0:
        negetive_value = True
        changed_value_percentage = changed_value_percentage * -1

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

news = []


def raw_text(data: str):
    soup = BeautifulSoup(data, "lxml")
    soup.a.decompose()
    data = soup.text + "\n"
    return data


news_api = "https://newsapi.org/v2/everything"
news_api_key = "889635b797c9442f984a5de1294da4f3"
news_api_parameters = {
    "from": news_date,
    "apikey": news_api_key,
    "q": COMPANY_NAME,
    "sortBy": "popularity"
}

with requests.get(news_api, news_api_parameters) as file:
    for i in range(1):
        description = raw_text(file.json()["articles"][i]["description"]) + "\n "
        title = file.json()["articles"][i]["title"] + "\n"
        data = {
            "title": title,
            "description": description
        }
        news.append(data)

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


message = STOCK + ": " + ("🔻" if negetive_value else "🔺") + str(changed_value_percentage) + "%" + "\n"


for data in news:
    message += "Headline: " + data["title"]
    message += "Brief: " + data["description"] + "\n"

account_sid = "AC4c6e2c531157a7e579ee5915c372818a"
auth_token = "e51fb3180f0caa014631b0338307a635"
twilio_number = "+12056276309"
sending_number = "+918415957390"

client = Client(account_sid, auth_token)

client.messages.create(
    body="\n" + message,
    from_=twilio_number,
    to=sending_number
)

# Optional: Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
