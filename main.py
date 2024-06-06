# streamlit_app.py
import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from streamlit_gsheets import GSheetsConnection

@st.cache_resource
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(usecols=[0, 1, 2, 3])
    df = df.dropna(subset=['date'])
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df.drop_duplicates(subset=['date', 'name'], keep='first', inplace=True)
    return df

df = load_data()

# 현재 날짜 가져오기
current_date = datetime.datetime.today().date()
# 현재 날짜에서 하루를 뺀 어제의 날짜 구하기
yesterday_date = current_date - datetime.timedelta(days=1)
# 데이터프레임에서 최대 날짜를 가져와서 날짜 부분만 추출
updated_date = df['date'].max().date()

# Title
st.title('출석수 카운트.B.01')

# Date selection widgets
start_date = st.date_input('이벤트 시작일', datetime.date(2024, 4, 24))
end_date = st.date_input('이벤트 종료일', updated_date)
# 날짜 변환
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Update Date
st.write("<h3>데이터 조회일 : {}~{}</h3>".format(start_date.date(), end_date.date()), unsafe_allow_html=True)

# Filtering based on date range
filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# 출석 많이 한 사람~!
top_cnt_users = filtered_df['name'].value_counts().reset_index()[:7]
top_cnt_users = top_cnt_users.sort_values(by='name', ascending=True)
# 시각화
fig_cnt = px.bar(x=top_cnt_users['name'], y=top_cnt_users['index'], orientation='h')
fig_cnt.update_traces(marker_color='blueviolet')
fig_cnt.update_layout(title='출석 많이 한 사람~!', xaxis_title = 'Count' ,yaxis_title='User')
st.plotly_chart(fig_cnt)

# 출석 빨리 한 사람~!
top_fast_users = filtered_df[filtered_df['idx'] == 1]['name'].value_counts()[:5].sort_values(ascending=True)
# 시각화
fig_fast = px.bar(x=top_fast_users.values, y=top_fast_users.index, orientation='h')
fig_fast.update_layout(title='출석 빨리 한 사람~!', xaxis_title = 'Count' ,yaxis_title='User')
st.plotly_chart(fig_fast)

# 날짜별 유저 수 집계
daily_users = filtered_df.groupby('date')['name'].nunique()

# Plotly를 사용하여 라인 그래프 생성
fig = px.line(x=daily_users.index, y=daily_users.values, labels={'x': 'Date', 'y': 'User Count'})
fig.update_layout(title='일별 출석수', xaxis_title='날짜', yaxis_title='사용자 수')
st.plotly_chart(fig)
