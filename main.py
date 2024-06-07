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
# 데이터프레임에서 최대 날짜를 가져와서 날짜 부분만 추출
updated_date = df['date'].max().date()
min_date = df['date'].min().date()
updated_date_d_1 = updated_date + datetime.timedelta(days=1)

# Title
st.title('출석수 카운트.B.03')

# Date selection widgets
start_date = st.date_input('이벤트 시작일', datetime.date(2024, 4, 24))
end_date = st.date_input('이벤트 종료일', updated_date)
end_date_str = end_date
# 날짜 변환
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

if (start_date > end_date) or (min_date > start_date):
    st.error('시작일 다시 선택 해주세요.')
elif start_date == end_date:
    st.success('데이터 조회일 : {}'.format(start_date.date()))
    one_date = df[df['date'] == start_date]
    one_date = one_date.copy()  # copy() 메서드를 사용하여 슬라이싱된 DataFrame의 복사본을 생성
    one_date['date'] = one_date['date'].apply(lambda x: pd.to_datetime(x).strftime('%Y-%m-%d'))
    st.write('출석 한 사람 : ', str(one_date.shape[0]), '명')
    st.dataframe(one_date)

elif updated_date < end_date:
    st.warning('{} 이후 데이터가 없습니다.'.format(updated_date_d_1))
else:
    # Update Date
    st.success("데이터 조회일 : {}~{}".format(start_date.date(), end_date.date()))

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
