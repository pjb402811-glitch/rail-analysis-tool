import streamlit as st
import sys
import os

# 1. 가장 먼저 페이지 설정을 합니다.
st.set_page_config(page_title="진단 모드")

st.title("🚀 시스템 진단 중...")

# 2. 현재 환경 정보 출력
st.write(f"파이썬 버전: {sys.version}")
st.write(f"현재 작업 디렉토리: {os.getcwd()}")
st.write(f"폴더 내 파일 목록: {os.listdir('.')}")

# 3. 핵심 모듈 임포트 시도 및 에러 포착
try:
    st.write("데이터 매니저(m1) 불러오는 중...")
    from m1 import DataManager
    st.success("✅ m1 임포트 성공!")
    
    st.write("설문 분석기(m6) 불러오는 중...")
    from m6 import SurveyAnalyzer
    st.success("✅ m6 임포트 성공!")
    
    st.write("PDF 생성기(m5) 불러오는 중...")
    from m5 import ProjectRecommender
    st.success("✅ m5 임포트 성공!")

except Exception as e:
    st.error("❌ 에러 발생!")
    st.exception(e)

st.info("이 화면이 보인다면 서버 연결은 정상입니다. 위 체크리스트 중 '❌'가 뜬 부분을 확인해 주세요.")
