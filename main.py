import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# ==========================================
# 1. 페이지 설정 및 초기화
# ==========================================
st.set_page_config(page_title="Optimized 3D N-Body Sim", layout="wide")

# ==========================================
# 2. 사이드바 설정 (컨트롤러)
# ==========================================
with st.sidebar:
    st.title("🌌 3D 시뮬레이션 설정")
    start_btn = st.button("🚀 시뮬레이션 시작", use_container_width=True)
    st.divider()
    G = st.slider("중력 상수 (G)", 0.1, 10.0, 2.0, 0.5)
    dt = st.slider("시간 간격 (dt)", 0.001, 0.05, 0.01, 0.001, format="%.3f")
    steps = st.slider("총 스텝 수", 100, 2000, 600, 100)
    
    st.divider()
    st.subheader("⏱️ 애니메이션 속도 제어")
    render_ratio = st.slider("몇 스텝마다 화면을 갱신할까요?", 1, 20, 5)
    fps_control = st.slider("프레임당 지연 시간 (초)", 0.000, 0.100, 0.005, 0.005, format="%.3f")

# ==========================================
# 3. 고속 3D 물리 엔진 (NumPy 벡터화 연산)
# ==========================================
def get_acc_3d_vectorized(pos, mass, G):
    N = pos.shape[0]
    diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
    dist_sq = np.sum(diff**2, axis=-1) + 0.01
    dist = np.sqrt(dist_sq)
    
    inv_dist_cube = np.where(dist > 0.1, 1.0 / (dist**3), 0.0)
    acc_matrix = G * mass[:, np.newaxis, np.newaxis] * diff * inv_dist_cube[:, :, np.newaxis]
    
    acc = np.sum(acc_matrix, axis=0)
    return acc

# ==========================================
# 4. 메인 대시보드 UI 구성
# ==========================================
st.title("🪐 실시간 3D N-Body 물리 시뮬레이션")
st.caption("텍스트 노출 오류를 수정하고 차트 출력 컨테이너를 정상 분리한 버전입니다.")

# ⚠️ 중요: 차트가 그려질 전용 독립 공간 선언
plot_spot = st.empty()

# 천체 초기 조건 정의
pos = np.array([
    [0.0, 0.0, 0.0],    # 중앙 천체
    [3.0, 0.0, 0.5],    # 행성 A
    [-3.0, 0.0, -0.5]   # 행성 B
])
vel = np.array([
    [0.0, 0.0, 0.0],
