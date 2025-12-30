# -*- coding: utf-8 -*-
# M1: 데이터 매니저 (정책 DB 로드) - Streamlit Cloud 최적화 버전
import pandas as pd
import os
import streamlit as st

class DataManager:

    KPI_ABBREVIATIONS = {
        "물리적 접근성": "PAI",
        "시간적 접근성": "TAI",
        "경제적 접근성": "EAI",
        "운행횟수": "TF",
        "표정속도": "TV",
        "열차운행 정시성": "TOTP",
        "환승시설 편의성": "TCI",
        "역사 시설 쾌적성": "SC",
        "열차이용 쾌적성": "TC",
        "환승시설 쾌적성": "TPC"
    }
    
    TCI_ALL_MODES = ['대중교통', '도보', '승용차', '택시/배웅', 'PM']
    
    ABBREVIATIONS_TO_FULL_NAMES = {v: k for k, v in KPI_ABBREVIATIONS.items()}

    def __init__(self):
        # --- [수정된 부분] 복잡한 경로 함수 제거하고 단순화 ---
        # 리눅스 서버에서는 그냥 "폴더명/파일명"으로 쓰면 알아서 찾습니다.
        
        # 1. 원본 파일 경로
        self.original_policy_path = "data/policy_db.csv"
        self.original_coeffs_path = "data/coefficients.csv"

        # 2. 수정 파일 경로
        self.modified_policy_path = "data/policy_db_modified.csv"
        self.modified_coeffs_path = "data/coefficients_modified.csv"

        # data 폴더가 혹시 없으면 에러가 나므로 확인
        if not os.path.exists('data'):
            os.makedirs('data')

    def _load_csv_with_encoding_fallback(self, filepath):
        """인코딩 폴백을 사용하여 CSV(쉼표 구분) 파일을 로드합니다."""
        if not os.path.exists(filepath):
            return None # 파일이 없으면 None 반환

        try:
            df = pd.read_csv(filepath, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='cp949')
        return df

    def _load_tsv_with_encoding_fallback(self, filepath):
        """인코딩 폴백을 사용하여 TSV(탭 구분) 파일을 로드합니다."""
        if not os.path.exists(filepath):
            return None

        try:
            df = pd.read_csv(filepath, encoding='utf-8', sep='\t')
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='cp949', sep='\t')
        return df

    def load_policy_data(self):
        """
        추진 과제(정책) 리스트를 로드합니다.
        """
        # 1. 수정된 파일이 있는지 먼저 확인
        if os.path.exists(self.modified_policy_path):
            df = self._load_csv_with_encoding_fallback(self.modified_policy_path)
        else:
            # 2. 없으면 원본 로드
            df = self._load_csv_with_encoding_fallback(self.original_policy_path)
        
        # 만약 원본도 못 찾으면 에러 방지를 위해 빈 데이터프레임 생성
        if df is None:
            st.error(f"🚨 데이터 파일을 찾을 수 없습니다: {self.original_policy_path}")
            return pd.DataFrame()

        df['duration_months'] = df['duration_months'].astype(str).str.replace('개월', '')
        df['duration_months'] = pd.to_numeric(df['duration_months'], errors='coerce').fillna(0).astype(int)
        return df

    def save_policy_data(self, df):
        df.to_csv(self.modified_policy_path, index=False, encoding='utf-8')

    def load_coefficients_df(self):
        """ 계수 파일을 로드합니다. """
        if os.path.exists(self.modified_coeffs_path):
            df = self._load_tsv_with_encoding_fallback(self.modified_coeffs_path)
        else:
            df = self._load_tsv_with_encoding_fallback(self.original_coeffs_path)
        
        if df is None:
            st.error(f"🚨 계수 파일을 찾을 수 없습니다: {self.original_coeffs_path}")
            return pd.DataFrame() # 빈 껍데기 반환

        return df

    def load_coefficients(self):
        """ 만족도 모형 계수 로드 및 변환 """
        df = self.load_coefficients_df()
        
        if df.empty:
            return {}, {}, {} # 파일 없으면 빈 딕셔너리 반환

        if 'model_type' not in df.columns:
            df['model_type'] = 'A'

        coeffs = {"S_max": 10.0, "coefficients": {}}
        pai_coeffs = {'weights': {}, 'alpha': {}}
        tci_coeffs = {}

        for _, row in df.iterrows():
            rail_type = row['rail_type']
            kpi = row['kpi']
            model_type = row.get('model_type', 'A')
            param1_name = row['param1_name']
            param1_value = row['param1_value']
            param2_name = row['param2_name']
            param2_value = row['param2_value']

            if kpi == 'PAI':
                if str(param1_name).startswith('w_'):
                    mode_name = param1_name[2:]
                    if rail_type not in pai_coeffs['weights']:
                        pai_coeffs['weights'][rail_type] = {}
                    pai_coeffs['weights'][rail_type][mode_name] = float(param1_value)
                elif param1_name == 'alpha':
                    pai_coeffs['alpha'][rail_type] = float(param1_value)
            
            elif kpi == 'TCI':
                if rail_type not in tci_coeffs:
                    tci_coeffs[rail_type] = {'P': {}, 'c': {}}
                
                if param1_name == 'S_max':
                    tci_coeffs['S_max'] = float(param1_value)
                elif str(param1_name).startswith('P_'):
                    mode = param1_name[2:]
                    tci_coeffs[rail_type]['P'][mode] = float(param1_value)
                elif str(param1_name).startswith('c_'):
                    mode = param1_name[2:]
                    tci_coeffs[rail_type]['c'][mode] = float(param1_value)

            if rail_type not in coeffs['coefficients']:
                coeffs['coefficients'][rail_type] = {}
            if kpi not in coeffs['coefficients'][rail_type]:
                coeffs['coefficients'][rail_type][kpi] = {
                    'model_type': model_type,
                    'params': {}
                }
            
            params_dict = coeffs['coefficients'][rail_type][kpi]['params']
            if pd.notna(param1_name) and pd.notna(param1_value):
                if not (kpi == 'TCI' and (str(param1_name).startswith('P_') or str(param1_name).startswith('c_'))):
                    params_dict[param1_name] = float(param1_value)
            if pd.notna(param2_name) and pd.notna(param2_value):
                params_dict[param2_name] = float(param2_value)

        # 하드코딩된 PAI 가중치 (백업용)
        pai_coeffs['weights'] = {
            '고속철도': {'도보': 10.28, '택시': 26.64, '승용차': 20.56, '자전거': 0.47, '공유PM': 0.47, '마을/시내버스': 18.22, '광역버스': 4.21, '지하철/광역철도': 19.16},
            '일반철도': {'도보': 5.97, '택시': 30.59, '승용차': 23.13, '자전거': 2.24, '공유PM': 1.49, '마을/시내버스': 27.61, '광역버스': 5.22, '지하철/광역철도': 3.73},
            '광역철도': {'도보': 39.06, '택시': 9.67, '승용차': 6.81, '자전거': 5.38, '공유PM': 3.58, '마을/시내버스': 23.66, '광역버스': 3.58, '지하철/광역철도': 8.24}
        }
        pai_coeffs['alpha'] = {'고속철도': 1.0, '일반철도': 1.0, '광역철도': 1.0}
                
        return coeffs, pai_coeffs, tci_coeffs
        
    def save_coefficients(self, df):
        df.to_csv(self.modified_coeffs_path, index=False, encoding='utf-8')

    def restore_policy_data(self):
        try:
            if os.path.exists(self.modified_policy_path):
                os.remove(self.modified_policy_path)
                st.toast("✅ 추진 과제 데이터가 초기 상태로 복원되었습니다.")
            else:
                st.toast("ℹ️ 이미 초기 상태입니다.")
        except Exception as e:
            st.error(f"🚨 복원 오류: {e}")

    def restore_coefficients_data(self):
        try:
            if os.path.exists(self.modified_coeffs_path):
                os.remove(self.modified_coeffs_path)
                st.toast("✅ 만족도 계수 데이터가 초기 상태로 복원되었습니다.")
            else:
                st.toast("ℹ️ 이미 초기 상태입니다.")
        except Exception as e:
            st.error(f"🚨 복원 오류: {e}")

    def restore_all_data(self):
        try:
            files_removed = False
            if os.path.exists(self.modified_policy_path):
                os.remove(self.modified_policy_path)
                files_removed = True
            if os.path.exists(self.modified_coeffs_path):
                os.remove(self.modified_coeffs_path)
                files_removed = True
            
            if files_removed:
                st.toast("✅ 모든 데이터가 초기 상태로 복원되었습니다.")
            else:
                st.toast("ℹ️ 이미 모든 데이터가 초기 상태입니다.")
        except Exception as e:
            st.error(f"🚨 복원 오류: {e}")