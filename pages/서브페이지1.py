import streamlit as st

st.set_page_config(  # 페이지 설정
    page_title="서브페이지",  # 페이지 Tab의 타이틀
    page_icon="smile",  # 페이지 Tab의 아이콘
    layout="centered",  # 페이지 레이아웃: centered, wide
    initial_sidebar_state="collapsed"
)

"# 서브페이지에 오신걸 환영합니다."

# 사이드바 설정
st.sidebar.title('다양한 사이드바 위젯들')

st.sidebar.checkbox('ㅈㅈㅈ')
st.sidebar.checkbox('345')

st.sidebar.divider()  # 구분선

st.sidebar.radio('데이터 타입', ['전체', '남성', '여성'])
st.sidebar.slider('나이', 0, 100, (20, 50))
st.sidebar.selectbox('지역', ['서울', '경기', '인천', '대전', '대구', '부산', '광주'])


