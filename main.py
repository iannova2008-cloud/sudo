import streamlit as st
import pandas as pd

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="전기차 화재 종합 현황 대시보드", layout="wide")
st.title("🚗 전기차 화재 발생 현황 종합 대시보드")
st.markdown("소방청 데이터를 기반으로 화재 발생 날짜, 지역, 발화 요인, 차량 상태 및 발화 지점의 관계를 분석합니다.")

# 2. 대한민국 주요 시도별 중심 위도/경도 데이터 매핑 (탭1 지도 시각화용)
geo_coords = {
    '서울특별시': [37.5665, 126.9780],
    '부산광역시': [35.1796, 129.0756],
    '대구광역시': [35.8714, 128.6014],
    '인천광역시': [37.4563, 126.7052],
    '광주광역시': [35.1595, 126.8526],
    '대전광역시': [36.3504, 127.3848],
    '울산광역시': [35.5389, 129.3114],
    '세종특별자치시': [36.4800, 127.2890],
    '경기도': [37.4138, 127.5183],
    '강원특별자치도': [37.8228, 128.1555],
    '충청북도': [36.6356, 127.4913],
    '충청남도': [36.5184, 126.8000],
    '전북특별자치도': [35.7175, 127.1530],
    '전라남도': [34.8679, 126.9910],
    '경상북도': [36.5760, 128.5056],
    '경상남도': [35.4606, 128.2132],
    '제주특별자치도': [33.4996, 126.5312]
}

# 3. 데이터 로드 함수 (인코딩 자동 예외 처리 및 월 추출 포함)
@st.cache_data
def load_data():
    file_path = "소방청_전기차 화재 발생 현황_20241231.csv"
    try:
        df = pd.read_csv(file_path, encoding="cp949")
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding="utf-8")
        
    # 날짜 컬럼 파싱 및 '월(Month)' 데이터 생성
    df['화재발생년월일'] = pd.to_datetime(df['화재발생년월일'])
    df['발생월'] = df['화재발생년월일'].dt.strftime('%m월')
    
    # 위도(latitude), 경도(longitude) 매핑
    df['latitude'] = df['시도'].map(lambda x: geo_coords.get(x, [None, None])[0])
    df['longitude'] = df['시도'].map(lambda x: geo_coords.get(x, [None, None])[1])
    
    return df

# 데이터 로드 실행
try:
    data = load_data()
except FileNotFoundError:
    st.error("⚠️ '소방청_전기차 화재 발생 현황_20241231.csv' 파일을 찾을 수 없습니다. 파일 이름을 확인해 주세요.")
    st.stop()

# 4. 3개의 탭 구성
tab1, tab2, tab3 = st.tabs(["📅 탭1: 날짜와 지역", "🔥 탭2: 발화 요인", "⚙️ 탭3: 차량 상태 · 발화 지점"])

# ==========================================
# [탭1: 날짜와 지역]
# ==========================================
with tab1:
    st.header("📅 날짜 및 지역별 화재 현황")
    
    # ① 월별 화재 발생 건수 (막대그래프)
    st.subheader("① 1년간 화재 발생 날짜 월별 현황 (막대그래프)")
    month_counts = data['발생월'].value_counts().sort_index().reset_index()
    month_counts.columns = ['발생월', '화재건수']
    st.bar_chart(month_counts.set_index('발생월'))

    st.markdown("---")
    
    # ② 대한민국 지도 산점도 (건수 기반 원 크기 조절 제공)
    st.subheader("② 1년간 화재 발생 지역 대한민국 지도 (산점도)")
    region_summary = data['시도'].value_counts().reset_index()
    region_summary.columns = ['시도', '화재건수']
    region_summary['latitude'] = region_summary['시도'].map(lambda x: geo_coords.get(x, [None, None])[0])
    region_summary['longitude'] = region_summary['시도'].map(lambda x: geo_coords.get(x, [None, None])[1])
    region_summary = region_summary.dropna(subset=['latitude', 'longitude'])
    
    # 지도 위에 표현될 원의 반지름 설정 (기본 3000배율)
    region_summary['size'] = region_summary['화재건수'] * 3000
    region_summary['color'] = "#FF4B4BA0"  # 반투명 빨간색
    
    st.map(region_summary, latitude='latitude', longitude='longitude', size='size', color='color')

    st.markdown("---")
    
    # ③ 지역별 화재 발생 지역 (선그래프)
    st.subheader("③ 1년간 화재 발생 지역 (선그래프)")
    # 인덱스를 '시도'로 설정해 축 이름을 명확히 지정
    st.line_chart(region_summary.set_index('시도')[['화재건수']])


# ==========================================
# [탭2: 발화 요인]
# ==========================================
with tab2:
    st.header("🔥 발화 요인 심층 분석")
    
    # ① 발화 요인 대분류별 (막대그래프)
    st.subheader("① 발화 요인 대분류별 현황 (막대그래프)")
    cause_large = data['발화요인대분류'].value_counts().reset_index()
    cause_large.columns = ['발화요인대분류', '화재건수']
    st.bar_chart(cause_large.set_index('발화요인대분류'))
    
    st.markdown("---")
    
    # ② 발화 요인 소분류 열람
    st.subheader("② 발화 요인 소분류 세부 열람 테이블")
    st.markdown("대분류와 매핑되는 소분류의 세부 발생 건수 테이블입니다. 표 우측 상단 단추로 정렬이 가능합니다.")
    cause_detail = data.groupby(['발화요인대분류', '발화요인소분류']).size().reset_index(name='발생건수')
    st.dataframe(cause_detail, use_container_width=True)


# ==========================================
# [탭3: 차량 상태, 발화 지점]
# ==========================================
with tab3:
    st.header("⚙️ 차량 상태 및 발화 지점 관계 현황")
    
    # ① 차량 상태별 시각화 
    st.subheader("① 차량 상태별 분포")
    status_counts = data['차량상태'].value_counts().reset_index()
    status_counts.columns = ['차량상태', '화재건수']
    
    # 주의: 순수 Streamlit과 Pandas 환경에서 st.pyplot이나 외부 차트 라이브러리(Matplotlib 등)를
    # 완벽히 배제하기 위해, 원그래프(Pie chart) 대안으로 가장 깔끔한 데이터프레임 도넛차트 형태의 
    # st.dataframe 프로그레스 바 표현식 또는 st.bar_chart를 권장하나, 
    # 요구사항을 직관적으로 수용하도록 정량적 수치 표와 누적 비중을 함께 제공합니다.
    st.write("차량 상태별 비율 분배 테이블:")
    status_counts['비율(%)'] = (status_counts['화재건수'] / status_counts['화재건수'].sum() * 100).round(1)
    st.dataframe(status_counts.set_index('차량상태'), use_container_width=True)
    
    # 대안 막대그래프도 시각적 보완용으로 배치
    st.bar_chart(status_counts.set_index('차량상태')[['화재건수']])
    
    st.markdown("---")
    
    # ② 발화 지점별 (막대그래프)
    st.subheader("② 차량 발화 지점별 현황 (막대그래프)")
    point_counts = data['차량발화지점'].value_counts().reset_index()
    point_counts.columns = ['차량발화지점', '화재건수']
    st.bar_chart(point_counts.set_index('차량발화지점'))
    
    # 💡 [보너스 분석 섹션] 차량 상태와 발화 지점 간의 교차 테이블
    with st.expander("🔍 [상세 분석] 차량 상태 X 차량 발화지점의 상관관계 행렬 보기"):
        cross_tab = pd.crosstab(data['차량상태'], data['차량발화지점'])
        st.dataframe(cross_tab, use_container_width=True)
