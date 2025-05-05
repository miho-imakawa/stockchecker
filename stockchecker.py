import pandas as pd
import altair as alt
import yfinance as yf
import streamlit as st

# タイトル
st.title("米国株価可視化アプリ")

# サイドバーを作成
st.sidebar.write("""
# 米国主要株価
株価の可視化を行います。
""")

st.sidebar.write("""
## 表示日数選択
""")

#　日数選択、1－50日まで、20はデフォルト値
days = st.sidebar.slider('日数', 1, 50, 20)

# fを入れることによってsidebarに連携
st.write(f"""
### 過去 **{days}日間** の米国主要株の株価
""")

#　キャッシュを残して、データの取得速度を上げる
@st.cache_data
# defで関数を入れる
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = "Name"
        df = pd.concat([df, hist])
    return df

try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)

    #　株価の範囲指定、0.0-3500.0まで、デフォルトは0.0-3500.0
    ymin, ymax = st.sidebar.slider(
        '株価の範囲指定',
        0.0, 3500.0, (0.0, 3500.0)
    )
    #　選択できる企業
    tickers = {
        'apple': 'AAPL',
        'microsoft': 'MSFT',
        'google': 'GOOGL',
        'amazon': 'AMZN',
        'meta': 'META',
        'nvidia': 'NVDA',
        'tesla': 'TSLA',
        'netflix': 'NFLX'
    }

    df = get_data(days, tickers)
    companies = st.multiselect(
        '会社名を選択してください',
        list(df.index),
        ['google', 'apple', 'meta', 'amazon']
    )

    if not companies:
        st.error("少なくとも一社選択してください")
    else:
        data = df.loc[companies]
        st.write("### 株価（USD）", data.sort_index())
        data = data.T.reset_index()
        #　データの整形
        data = pd.melt(data, id_vars=['Date']).rename(
        columns={'value': 'Stock Prices(USD)'}
        )   
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x="Date:T",
                y=alt.Y("Stock Prices(USD):Q", stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        "エラーが発生しました。もう一度お試しください。"
    )