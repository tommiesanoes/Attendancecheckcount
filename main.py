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

# 캐시를 초기화할지 여부를 확인하는 함수
def check_cache():
    # 현재 시간 가져오기
    now = datetime.datetime.now()

    # 캐시 타임스탬프가 없거나 하루 이상 지났다면 캐시를 초기화
    if 'cache_timestamp' not in st.session_state or (now - st.session_state.cache_timestamp).days >= 1:
        st.cache_resource.clear()
        st.session_state.cache_timestamp = now

# 캐시를 확인하고 초기화할지 결정
check_cache()

# 데이터 로드
df = load_data()

# 현재 날짜
current_date = datetime.datetime.today().date()
# 데이터프레임에서 최대 날짜 가져오기
updated_date = df['date'].max().date()
min_date = df['date'].min().date()
updated_date_d_1 = updated_date + datetime.timedelta(days=1)

# 제목
st.title('출석수 카운트.B.0.4')

# 날짜 선택 위젯
start_date = st.date_input('이벤트 시작일', datetime.date(2024, 4, 24))
end_date = st.date_input('이벤트 종료일', updated_date)
end_date_str = end_date
# 날짜 변환
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Adjusting date comparison to avoid FutureWarning
if (start_date.date() > end_date.date()) or (min_date > start_date.date()) or (start_date.date() > updated_date):
    st.error('시작일 다시 선택 해주세요.')
elif start_date.date() == end_date.date():
    st.success('데이터 조회일 : {}'.format(start_date.date()))
    one_date = df[df['date'].dt.date == start_date.date()]
    one_date = one_date.copy()  # 슬라이스된 DataFrame의 복사본 생성
    one_date['date'] = one_date['date'].apply(lambda x: pd.to_datetime(x).strftime('%Y-%m-%d'))
    st.write('출석 한 사람 : ', str(one_date.shape[0]), '명')
    st.dataframe(one_date)
elif updated_date < end_date.date():
    st.warning('{} 이후 데이터가 없습니다.'.format(updated_date_d_1))
else:
    # 날짜 업데이트
    st.success("데이터 조회일 : {}~{}".format(start_date.date(), end_date.date()))

    # 날짜 범위에 따라 필터링
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # 출석 많이 한 사람
    top_cnt_users = filtered_df['name'].value_counts().reset_index()[:7]
    top_cnt_users = top_cnt_users.sort_values(by='name', ascending=True)
    # 시각화
    fig_cnt = px.bar(x=top_cnt_users['name'], y=top_cnt_users['index'], orientation='h')
    fig_cnt.update_traces(marker_color='blueviolet')
    fig_cnt.update_layout(title='출석 많이 한 사람~!', xaxis_title = 'Count' ,yaxis_title='User')
    st.plotly_chart(fig_cnt)

    # 출석 빨리 한 사람
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
