import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. 페이지 설정
st.set_page_config(page_title="Optimized 3D N-Body Sim", layout="wide")

# 2. 사이드바 설정
with st.sidebar:
    st.title("🌌 3D 시뮬레이션 설정")
    start_btn = st.button("🚀 시뮬레이션 시작", use_container_width=True)
    st.divider()
    G = st.slider("중력 상수 (G)", 0.1, 10.0, 2.0, 0.5)
    dt = st.slider("시간 간격 (dt)", 0.001, 0.05, 0.01, 0.001, format="%.3f")
    steps = st.slider("총 스텝 수", 100, 2000, 600, 100)
    
    st.divider()
    st.subheader("⏱️ 애니메이션 속도 제어")
    # 노트북 환경을 위해 프레임 스킵(render_ratio)을 조금 더 여유 있게 조절 가능하도록 설정
    render_ratio = st.slider("몇 스텝마다 화면을 갱신할까요?", 1, 20, 5)
    fps_control = st.slider("프레임당 지연 시간 (초)", 0.000, 0.100, 0.005, 0.005, format="%.3f")

# 3. 고속 3D 물리 엔진 (NumPy 벡터화로 for 루프 제거)
def get_acc_3d_vectorized(pos, mass, G):
    N = pos.shape[0]
    # 두 천체 간의 거리 벡터 계산 (N, N, 3)
    diff = pos[:, np.newaxis, :] - pos[np.newaxis, :, :]
    
    # 거리의 제곱 계산 후 Softening 추가
    dist_sq = np.sum(diff**2, axis=-1) + 0.01
    dist = np.sqrt(dist_sq)
    
    # 거리가 0이 되는 자기 자신과의 연산 분모 예외 처리 (1로 나눠지게 만듦)
    inv_dist_cube = np.where(dist > 0.1, 1.0 / (dist**3), 0.0)
    
    # 가속도 계산: G * m_j * diff_ij / dist_ij^3
    # mass[:, np.newaxis]를 곱해 각 천체의 질량 반영
    acc_matrix = G * mass[:, np.newaxis, np.newaxis] * diff * inv_dist_cube[:, :, np.newaxis]
    
    # 나에게 작용하는 힘들을 모두 합산 (i축 기준으로 합산하되 방향 부호 반전 고려)
    acc = np.sum(acc_matrix, axis=0)
    return acc

# 4. 메인 화면 구성
st.title("🪐 실시간 3D N-Body 물리 시뮬레이션 (노트북 최적화 버전)")
st.caption("NumPy 벡터화 연산과 데이터 선행 계산 기법을 적용하여 노트북 환경에서의 랙을 최소화했습니다.")

plot_spot = st.empty()

# 5. 초기 조건 설정
pos = np.array([
    [0.0, 0.0, 0.0],    # 중앙의 무거운 천체
    [3.0, 0.0, 0.5],    # 행성 A
    [-3.0, 0.0, -0.5]   # 행성 B
])
vel = np.array([
    [0.0, 0.0, 0.0],
    [0.0, 2.2, 0.5],
    [0.0, -2.2, -0.5]
])
mass = np.array([30.0, 3.0, 3.0])
colors = ['#FF4B4B', '#1C83E1', '#00C781']
names = ['중앙 천체', '행성 A', '행성 B']

# 6. 버튼 클릭 시 실행
if start_btn:
    # --- [최적화 핵심 1] 물리 경로 선행 계산 (Pre-computation) ---
    # 시뮬레이션 하면서 그리지 않고, 모든 좌표를 메모리에 먼저 초고속으로 계산해 둡니다.
    with st.spinner("🌌 우주의 궤적을 계산하는 중..."):
        history_pos = np.zeros((steps, len(pos), 3))
        acc = get_acc_3d_vectorized(pos, mass, G)
        
        for step in range(steps):
            pos = pos + vel * dt + 0.5 * acc * dt**2
            new_acc = get_acc_3d_vectorized(pos, mass, G)
            vel = vel + 0.5 * (acc + new_acc) * dt
            acc = new_acc
            history_pos[step] = pos  # 각 스텝의 위치 저장

    # --- [최적화 핵심 2] 렌더링 루프 최적화 ---
    # Plotly Figure 틀을 딱 한 번만 만듭니다.
    fig = go.Figure()
    
    # 초기 트레이스(천체들) 추가
    for i in range(len(pos)):
        fig.add_trace(go.Scatter3d(
            x=[history_pos[0, i, 0]], 
            y=[history_pos[0, i, 1]], 
            z=[history_pos[0, i, 2]],
            mode='markers',
            name=names[i],
            marker=dict(
                size=mass[i] * 0.8 + 5,
                color=colors[i],
                opacity=0.9,
                line=dict(color='white', width=1)
            )
        ))
        
    # 레이아웃 기본 설정 (이것도 한 번만 정의)
    fig.update
