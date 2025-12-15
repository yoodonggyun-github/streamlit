import streamlit as st

st.set_page_config(  # 페이지 설정
    page_title="유동균의 Streamlit",  # 페이지 Tab의 타이틀
    page_icon="",  # 페이지 Tab의 아이콘
    layout="wide",  # 페이지 레이아웃: centered, wide
    initial_sidebar_state="expanded",  # 사이드바 초기 상태
    menu_items={
        'Get help': "https://docs.streamlit.io",  # URL만
        'Report a bug': "https://streamlit.io",   # URL만
        
    }
)

# 데이터 받아오기
import os
import sys
# sys.path.append('../data')  # my_apikeys.py 파일이 있는 경로
# import my_apikeys as mykeys
import urllib.request
import urllib.parse
import pandas as pd
import json

# 네이버에서 발급받은 클라이언트 ID와 시크릿을 사용
client_id = 'VPW08RQ93DKQMDgsgl6R'
client_secret = 'GxDdXRVvwh'

# 파라미터 설정
display_count = 100  # 한 페이지에 표시할 검색 결과 수
num_data = 1000      # 검색할 데이터 개수
sort = 'date'        # 정렬 기준 (date: 날짜순, sim: 유사도순)

# 검색할 단어와 URL 설정
encText = urllib.parse.quote("K팝 데몬 헌터스")

# 결과를 저장할 list 생성
results = []

# for문을 사용하여 검색 결과를 페이지별로 요청
for idx in range(1, num_data + 1, display_count):

    # JSON 결과를 요청할 URL 생성
    url = "https://openapi.naver.com/v1/search/news?query=" + encText \
          + f"&start={idx}&display={display_count}&sort={sort}"

    # 요청 객체 생성
    request = urllib.request.Request(url)

    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)

    # 요청 보내서 응답 받기
    response = urllib.request.urlopen(request)
    rescode = response.getcode()

    if rescode == 200:  # 응답 코드가 200이면 성공
        # 응답 본문을 읽어옴
        response_body = response.read()
        # response_body는 바이트 문자열이므로 decode를 통해 문자열로 변환
        response_dict = json.loads(response_body.decode('utf-8'))
        # dictionary에서 'items' 키를 사용하여 뉴스 기사 목록을 가져옴
        results = results + response_dict['items']
    else:
        print("Error Code:" + str(rescode))

from datetime import datetime
import re

# 저장할 빈 데이터프레임 생성
df = pd.DataFrame()

# 문자열에서 제거할 tag를 지정.
remove_tags = re.compile(r'<.*?>')  # HTML 태그 제거를 위한 정규표현식

# 검색 결과에서 필요한 정보 추출
for item in results:
    # 각 뉴스 기사에서 필요한 정보 추출
    new_data = pd.DataFrame(
        data={
            # 날짜는 datetime 객체로 변환
            'pubDate': datetime.strptime(
                item['pubDate'], "%a, %d %b %Y %H:%M:%S +0900"
            ),
            # title과 description에서 HTML 태그 제거
            'title': re.sub(remove_tags, '', item['title']),
            'description': re.sub(remove_tags, '', item['description'])
        },
        index=[0]  # index를 0으로 설정하여 단일 행 데이터프레임 생성
    )

    # 데이터프레임에 추가
    df = pd.concat([df, new_data], ignore_index=True)

df.to_csv('./demon.csv', index=False, encoding='utf-8')

# 사이드바 설정
st.title('C011124 유동균')

st.sidebar.title('다양한 사이드바 위젯들')

#  워드클라우드
from wordcloud import WordCloud, STOPWORDS

with open('./불용어.txt', 'r', encoding='utf-8') as f:
    stopwords = f.read().splitlines()

text = ' '.join(df['description'].dropna().tolist())

han_font_path = './malgun.ttf'

import matplotlib.pyplot as plt

# 한글 폰트 경로를 지정한 워드클라우드 객체 생성
words_han = WordCloud(
    font_path=han_font_path,   # 한글 폰트 경로
    max_words=50,              # 최대 표시 단어 수
    width=800,
    height=800,
    stopwords=stopwords,       # 불용어 설정
    background_color='black',  # 배경색
    colormap='coolwarm'        # 컬러맵
).generate(text)


'## :orange[체크박스]'
check1 = st.checkbox('워드클라우드 보기')

if check1:
    st.write('체크되었습니다.')

    fig, ax = plt.subplots()
    ax.imshow(words_han)

    st.pyplot(fig) # 차트 출력
    st.divider() # 구분선
    
check2= st.checkbox('네트워크 시각화 보기')

if check2:
    st.write('체크되었습니다.')

    # 네트워크 시각화
    edge_list = []

    from itertools import combinations
    from collections import Counter
    import networkx as nx
    from konlpy.tag import Okt
    import re

    okt = Okt()

    descriptions = df['description'].tolist()
    all_nouns = []
    for i, text in enumerate(descriptions):
        # 정제: 한글과 공백을 제외한 모든 문자 제거
        text_cleaned = re.sub(r'[^가-힣\s]', '', text)
        # 형태소 분리 후 명사만 추출
        nouns = okt.nouns(text_cleaned)

        nouns = [word for word in set(nouns) if (len(word) > 1) and (word not in stopwords)]
        #전처리된 단어목록을 all_words에 추가
        all_nouns.append(nouns)

    # 각 문서의 명사 목록에서 2-튜플 조합 생성
    for nouns in all_nouns:
        if len(nouns) > 1:  # 단어가 2개 이상인 경우에만 처리
            # 사전식으로 정렬한 후 조합을 생성하여 edge_list에 추가
            edge_list.extend(combinations(sorted(nouns), 2))

    # 생성된 edge 리스트의 중복 개수를 계산
    edge_counts = Counter(edge_list)

    #지정된 최소 빈도 이상의 엣지만 필터링
    min_count = 20
    filtered_edges = {edge: weight for edge, weight in edge_counts.items() if weight > min_count}

    #그래프 객체 생성
    G = nx.Graph()

    #가중치가 포함된 엣지 리스트 생성
    weighted_edges = [
        (node1, node2, weight)
        for (node1, node2), weight in filtered_edges.items()
    ]
    # 엣지와 가중치 추가
    G.add_weighted_edges_from(weighted_edges)

    # 레이아웃 생성
    pos_spring = nx.spring_layout(
        G,              # 그래프 객체
        k=0.3,           # 노드 간격 조절 파라미터
        iterations=50,   # 반복 횟수
        seed=42
    )

    # 노드 크기 설정 (차수 기반)
    node_sizes = [G.degree(node) * 100 for node in G.nodes()]

    # 엣지 두께 설정 (가중치 기반)
    edge_widths = [G[u][v]['weight'] * 0.05 for u, v in G.edges()]

    # 그래프 그리기
    fig, ax = plt.subplots(figsize = (15,15))

    nx.draw_networkx(
        G,
        pos_spring,
        with_labels=True,
        node_size=node_sizes,
        width=edge_widths,
        font_family='malgun gothic',
        font_size=12,
        node_color='skyblue',
        edge_color='gray',
        alpha=0.8
    )
    plt.axis('off')

    st.pyplot(fig)

check3= st.checkbox('plotly')

import plotly.express as px
from collections import Counter

if check3:
    st.write('체크되었습니다.')

    # WordCloud 객체에서 단어 빈도 가져오기
    words= WordCloud().generate(text)

    df = pd.DataFrame(words.words_.items(), columns=['word', 'freq'])
    df = df.head(20) 

    # Plotly 막대그래프
    fig = px.bar(
        df,
        x='word',
        y='freq',
        title='단어 빈도',
        labels={'freq':'빈도', 'word':'단어'}
    )
    st.plotly_chart(fig)

check4= st.checkbox('altair')

if check4:
    st.write('체크되었습니다.')
    
    import altair as alt
    # WordCloud 객체에서 단어 빈도 가져오기
    words= WordCloud().generate(text)

    df = pd.DataFrame(words.words_.items(), columns=['word', 'freq'])
    df = df.head(20) 

    # Plotly 막대그래프
    fig = px.bar(
        df,
        x='word',
        y='freq',
        title='단어 빈도',
        labels={'freq':'빈도', 'word':'단어'}
    )
    
    c = (
    alt.Chart(df)
    .mark_circle()
    .encode(
        x='word', 
        y='freq',                  
        size='freq',                
        color='freq',               
        tooltip=['word', 'freq'] 
        )
    )

    st.altair_chart(c, use_container_width=True)
    
check5= st.checkbox('seaborn')

if check5:
    st.write('체크되었습니다.')
    
    import seaborn as sns

# WordCloud 객체에서 단어 빈도 가져오기
    words= WordCloud().generate(text)

    df = pd.DataFrame(words.words_.items(), columns=['word', 'freq'])
    df = df.head(20) 

    # Plotly 막대그래프
    fig = px.bar(
        df,
        x='word',
        y='freq',
        title='단어 빈도',
        labels={'freq':'빈도', 'word':'단어'}
    )

    fig, ax = plt.subplots()

    sns.barplot(data=df, x='word', y='freq', ax=ax)
    
    st.pyplot(fig)

