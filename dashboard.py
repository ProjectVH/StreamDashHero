import streamlit as st
import pandas as pd
import numpy as np
import tweepy
import requests
import config
import psycopg2
import psycopg2.extras

auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY,
                           config.TWITTER_CONSUMER_SECRET)
auth.set_access_token(config.TWITTER_ACCESS_TOKEN,
                      config.TWITTER_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


option = st.sidebar.selectbox("Which Dashbboard", ('twitter',
                                                   'stocktwits'))

st.markdown("""
<style>
body {
  background: #fffff; 
}
</style>
    """, unsafe_allow_html=True)

st.header(option)

if option == 'twitter':
    for username in config.TWITTER_USERNAMES:
        user = api.get_user(username)
        tweets = api.user_timeline(username)

        st.subheader(username)
        st.image(user.profile_image_url)

        for tweet in tweets:
            if '$' in tweet.text:
                words = tweet.text.split(' ')
                for word in words:
                    if word.startswith('$') and word[1:].isalpha():
                        symbol = word[1:]
                        st.write(symbol)
                        st.write(tweet.text)
                        st.image(
                            f"https://charts2.finviz.com/chart.ashx?t={symbol}")


# This is conenect to the docker server (WSB tracker)
# IF change the content on wallstreetbet, you need to change the code on WSB tracker
if option == 'wallstreetbets':

    number_days = st.sidebar.slider('Number of days', 1, 30, 3)
    st.subheader('From 20th May till 31st May')
    cursor.execute("""
        SELECT count (*) as num_mentions, stock_id, symbol
        FROM mention JOIN stock ON stock.id = mention.stock_id
        WHERE date(dt) > current_date - interval '%s days'
        GROUP BY stock_id, symbol
        HAVING COUNT (symbol) > 10
        order by num_mentions DESC
    """, (number_days,))

    counts = cursor.fetchall()
    for count in counts:
        st.write(count)

    cursor.execute("""
        SELECT symbol , message, url, dt, username
        FROM mention JOIN stock on stock.id = mention.stock_id
        ORDER BY dt DESC
        LIMIT 100
    """)

    mentions = cursor.fetchall()
    for mention in mentions:
        st.text(mention['dt'])
        st.text(mention['symbol'])
        st.text(mention['message'])
        st.text(mention['url'])
        st.text(mention['username'])

    rows = cursor.fetchall()

    st.write(rows)

if option == 'stocktwits':
    symbol = st.sidebar.text_input("Symbol", value='AAPL', max_chars=5,
                                   key=None, type='default', help=None)
    # st.subheader('stocktwits')
    r = requests.get(
        f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")

    data = r.json()

    for message in data['messages']:
        st.image(message['user']['avatar_url'])
        st.write(message['user']['username'])
        st.write(message['created_at'])
        st.write(message['body'])


# The following two parts require paid version of alpaca trading account.

# if option == 'chart':
#     symbol = st.sidebar.text_input("Symbol", value='MSFT', max_chars=None, key=None, type='default')

#     data = pd.read_sql("""
#         select date(day) as day, open, high, low, close
#         from daily_bars
#         where stock_id = (select id from stock where UPPER(symbol) = %s)
#         order by day asc""", connection, params=(symbol.upper(),))

#     st.subheader(symbol.upper())

#     fig = go.Figure(data=[go.Candlestick(x=data['day'],
#                     open=data['open'],
#                     high=data['high'],
#                     low=data['low'],
#                     close=data['close'],
#                     name=symbol)])

#     fig.update_xaxes(type='category')
#     fig.update_layout(height=700)

#     st.plotly_chart(fig, use_container_width=True)

#     st.write(data)


# if option == 'pattern':
#     pattern = st.sidebar.selectbox(
#         "Which Pattern?",
#         ("engulfing", "threebar")
#     )

#     if pattern == 'engulfing':
#         cursor.execute("""
#                 SELECT *
#                 FROM (
#                     SELECT day, open, close, stock_id, symbol,
#                     LAG(close, 1) OVER ( PARTITION BY stock_id ORDER BY day ) previous_close,
#                     LAG(open, 1) OVER ( PARTITION BY stock_id ORDER BY day ) previous_open
#                     FROM daily_bars
#                     JOIN stock ON stock.id = daily_bars.stock_id
#                 ) a
#                 WHERE previous_close < previous_open AND close > previous_open AND open < previous_close
#                 AND day = '2021-02-18'
#             """)

#     if pattern == 'threebar':
#         cursor.execute("""
#                 SELECT *
#                 FROM (
#                     SELECT day, close, volume, stock_id, symbol,
#                     LAG(close, 1) OVER ( PARTITION BY stock_id ORDER BY day ) previous_close,
#                     LAG(volume, 1) OVER ( PARTITION BY stock_id ORDER BY day ) previous_volume,
#                     LAG(close, 2) OVER ( PARTITION BY stock_id ORDER BY day ) previous_previous_close,
#                     LAG(volume, 2) OVER ( PARTITION BY stock_id ORDER BY day ) previous_previous_volume,
#                     LAG(close, 3) OVER ( PARTITION BY stock_id ORDER BY day ) previous_previous_previous_close,
#                     LAG(volume, 3) OVER ( PARTITION BY stock_id ORDER BY day ) previous_previous_previous_volume
#                     FROM daily_bars
#                     JOIN stock ON stock.id = daily_bars.stock_id) a
#                     WHERE close > previous_previous_previous_close
#                     AND previous_close < previous_previous_close
#                     AND previous_close < previous_previous_previous_close
#                     AND volume > previous_volume
#                     AND previous_volume < previous_previous_volume
#                     AND previous_previous_volume < previous_previous_previous_volume
#                     AND day = '2021-02-19'
#             """)

#     rows = cursor.fetchall()

#     for row in rows:
#         st.image(f"https://finviz.com/chart.ashx?t={row['symbol']}")
