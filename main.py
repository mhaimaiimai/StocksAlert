import requests
from datetime import datetime, timedelta
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
STOCK_APIKEY = ""
CLOSING_P = "4. close"
CHANGE_THRESHOLD = 0.05

NEWS_APIKEY = ""
NEWS_LIMIT = 3

TWILIOSID = ""
TWILIOTOKEN = ""
TELFROM = ""
TELTO = ""


def check_stocks():
    
    stock_param = {"function" : "TIME_SERIES_DAILY_ADJUSTED",
                   "symbol" : STOCK,
                   "apikey" : STOCK_APIKEY}

    response = requests.get(STOCK_ENDPOINT, params=stock_param)
    response.raise_for_status()
    response_json = response.json()
    stock_data = response_json["Time Series (Daily)"]
    today = datetime.now().date()
    yesterday = today - timedelta(1)
    before_yesterday = yesterday - timedelta(1)

    try:
        data_yesterday = float(stock_data[str(yesterday)][CLOSING_P])
        data_before_yesterday = float(stock_data[str(before_yesterday)][CLOSING_P])
        
    except KeyError:
        return 0
        
    else:
        val_dif = round((data_yesterday - data_before_yesterday)/data_yesterday,2)
        if(abs(val_dif) >=CHANGE_THRESHOLD):
            return val_dif
        else:
            return 0
    

def check_news():
    news_param = {"q": COMPANY_NAME,
                  "from": str(before_yesterday),
                  "sortBy": "popularity",
                  "apiKey": NEWS_APIKEY}
    
    response = requests.get(NEWS_ENDPOINT, params=news_param)
    response.raise_for_status()
    response_json = response.json()
    news_data = response_json["articles"]
    return news_data[:NEWS_LIMIT]


def send_sms(msg_content):
    client = Client(TWILIOSID, TWILIOTOKEN)
    
    message = client.messages \
                    .create(
                        body=msg_content,
                        from_=TELFROM,
                        to=TELTO
                    )
    print(message.status)


def main():
    val_dif = check_stocks()
    if val_dif!=0:
        news_list = check_news()
        msg_title = f"{STOCK}: "
        if val_dif>0:
            msg_title += f"🔺{val_dif}%\n"
        else:
            msg_title += f"🔻{abs(val_dif)}%\n"
            
        for news in news_list:
            msg_body= msg_title+ f"Headline: {news['title']}\nBrief: {news['description']}"
            send_sms(msg_body)

main()