import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

# 현재 날짜 가져오기
current_date = datetime.date.today()
# 어제 날짜 계산
yesterday_date = current_date - datetime.timedelta(days=1)

# Load the data
df = pd.read_csv('attendance_data.csv')
df['date'] = pd.to_datetime(df['date']).dt.date  # Convert datetime to date
# Remove duplicates
df.drop_duplicates(subset=['date', 'name'], keep='last', inplace=True)

# Title
st.title('출석수 카운트.Beta')

# Date selection widgets
start_date = st.date_input('이벤트 시작일', datetime.date(2024, 4, 24))
end_date = st.date_input('이벤트 종료일', yesterday_date)

# Display the selected dates
st.write('업데이트일:', datetime.date(2024, 6, 4))
st.write('시작일:', start_date)
st.write('종료일:', end_date)

# Filtering based on date range
filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

top_5_count_users = filtered_df['name'].value_counts().reset_index()[:5]
top_5_count_users = top_5_count_users.sort_values(by='count', ascending=True)

# Plotly를 사용하여 수평 막대 그래프 생성
fig = px.bar(x=top_5_count_users['count'], y=top_5_count_users['name'], orientation='h')
# 막대의 색상을 연보라색으로 설정
fig.update_traces(marker_color='blueviolet')
fig.update_layout(title='출석 많이 한 사람~!', xaxis_title = 'Count' ,yaxis_title='User')
st.plotly_chart(fig)

# 시각화를 위한 데이터 처리
ranked_users = filtered_df.dropna(subset=['rank'])  # 결측값을 제외한 데이터
top_5_users = ranked_users[ranked_users['rank'] == '1등']['name'].value_counts()[:5].sort_values(ascending=True)

# Plotly를 사용하여 수평 막대 그래프 생성
fig = px.bar(x=top_5_users.values, y=top_5_users.index, orientation='h')
fig.update_layout(title='출석 빨리 한 사람~!', xaxis_title = 'Count' ,yaxis_title='User')
st.plotly_chart(fig)

# 날짜별 유저 수 집계
daily_users = filtered_df.groupby('date')['name'].count()

# Plotly를 사용하여 라인 그래프 생성
fig = px.line(x=daily_users.index, y=daily_users.values, labels={'x': 'Date', 'y': 'User Count'})
fig.update_layout(title='일별 출석수', xaxis_title='날짜', yaxis_title='사용자 수')
st.plotly_chart(fig)
