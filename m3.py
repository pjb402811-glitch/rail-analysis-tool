# -*- coding: utf-8 -*-
# M3: Main App (Router)
# 실행: streamlit run m3.py

import streamlit as st
import logging

# [수정] st.set_page_config는 반드시 다른 모듈(m3_1~4) 임포트보다 '먼저' 실행되어야 합니다.
# 이 순서가 틀리면 Streamlit Cloud에서 앱이 즉시 종료될 수 있습니다.
st.set_page_config(
    page_title="철도 정책 시뮬레이터",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 페이지 설정 이후에 모듈 임포트 진행
try:
    from m3_1 import initialize_session_state
    from m3_2 import draw_landing_page
    from m3_3 import draw_user_view
    from m3_4 import draw_admin_view
except ImportError as e:
    st.error(f"모듈을 불러오는 중 오류가 발생했습니다. 파일 이름을 확인해주세요: {e}")
    st.stop()

# --- 세션 상태 초기화 ---
# 앱 실행 시 최초 1회만 호출
initialize_session_state()

# --- 메인 라우터 ---
def main():
    """
    st.session_state.view_mode에 따라 적절한 UI를 렌더링합니다.
    """
    # 세션 상태에서 뷰 모드를 안전하게 가져옴
    view_mode = st.session_state.get('view_mode', 'landing')

    try:
        if view_mode == 'user':
            draw_user_view()
        elif view_mode == 'admin':
            draw_admin_view()
        else: # 'landing' or default
            draw_landing_page()
    except Exception as e:
        st.error(f"화면을 그리는 중 예상치 못한 오류가 발생했습니다: {e}")
        logging.error(f"Render Error: {e}")

if __name__ == "__main__":
    main()