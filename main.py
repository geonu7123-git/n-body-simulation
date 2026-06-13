import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. 페이지 설정
st.set_page_config(page_title="3D N-Body Sim", layout="wide")

# 2. 사이드바 설정
with st.sidebar:
    st.title("🌌 3D 시뮬레이션 설정")
    start_btn = st.button("🚀 시뮬레이션 시작", use_container_width=True)
    st.divider()
    G = st.slider("중력 상수 (G)", 0.1, 10.0, 2.0, 0.5)
    dt = st.slider("시간 간격 (dt)", 0.001, 0.05, 0.01, 0.001, format="%.3f")
    steps = st.slider("총 스텝 수", 100, 2000, 500, 100)
    
    st.divider()
    st.subheader("⏱️ 애니메이션 속도 제어")
    fps_control = st.slider("프레임당 지연 시간 (초)", 0.000, 0.100, 0.010, 0.005, format="%.3f")
    render_ratio = st.slider("몇 스텝마다 화면을 갱신할까요?", 1, 10, 2)
    
# 3. 3D 물리 엔진 함수 (Z축 연산 추가됨)
def get_acc_3d(pos, mass, G):
    N = pos.shape[0]
    acc = np.zeros_like(pos) # (N, 3) 형태
    for i in range(N):
        for j in range(N):
            if i != j:
                diff = pos[j] - pos[i]
                dist = np.linalg.norm(diff) + 0.1 # Softening (충돌 방지)
                acc[i] += G * mass[j] * diff / (dist**3)
    return acc

# 4. 메인 화면 구성
st.title("🪐 실시간 3D N-Body 물리 시뮬레이션")
st.caption("Plotly를 사용하여 3D 우주 공간을 구현했습니다. 마우스 드래그로 화면을 회전하거나 확대할 수 있습니다.")

plot_spot = st.empty() # 애니메이션이 그려질 자리

# 5. 3D 초기 조건 설정 (X, Y, Z축 데이터 구성)
# 위치(x, y, z), 속도(vx, vy, vz), 질량(m)
pos = np.array([
    [0.0, 0.0, 0.0],    # 중앙의 무거운 천체
    [3.0, 0.0, 0.5],    # 약간 비스듬하게 도는 천체 1
    [-3.0, 0.0, -0.5]   # 반대 방향으로 도는 천체 2
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
    acc = get_acc_3d(pos, mass, G) # 초기 3D 가속도
    
    for step in range(steps):
        # Velocity Verlet 알고리즘 기반 3D 위치 및 속도 업데이트
        pos = pos + vel * dt + 0.5 * acc * dt**2
        new_acc = get_acc_3d(pos, mass, G)
        vel = vel + 0.5 * (acc + new_acc) * dt
        acc = new_acc
        
        # 지정된 주기마다 3D 화면 새로 그리기
        if step % render_ratio == 0:
            # Plotly 3D Scatter 차트 생성
            fig = go.Figure()
            
            for i in range(len(pos)):
                fig.add_trace(go.Scatter3d(
                    x=[pos[i, 0]], y=[pos[i, 1]], z=[pos[i, z] for z in [pos[i, 2]]],
                    mode='markers',
                    name=names[i],
                    marker=dict(
                        size=mass[i] * 0.8 + 5, # 질량 비례 크기
                        color=colors[i],
                        opacity=0.9,
                        line=dict(color='white', width=1)
                    )
                ))
            
            # 3D 우주 공간 스타일 및 배경 설정 (다크 모드 적용)
            fig.update_layout(
                template="plotly_dark",
                margin=dict(l=0, r=0, b=0, t=40),
                scene=dict(
                    xaxis=dict(range=[-8, 8], backgroundcolor="rgba(0,0,0,0)", gridcolor="gray", showbackground=True),
                    yaxis=dict(range=[-8, 8], backgroundcolor="rgba(0,0,0,0)", gridcolor="gray", showbackground=True),
                    zaxis=dict(range=[-8, 8], backgroundcolor="rgba(0,0,0,0)", gridcolor="gray", showbackground=True),
                    aspectmode='cube'
                ),
                title=dict(text=f"📊 Simulation Step: {step} / {steps}", x=0.5, y=0.95),
                height=650
            )
            
            # Streamlit 웹페이지에 3D 차트 출력
            plot_spot.plotly_chart(fig, use_container_width=True)
            
            # 애니메이션 속도 제어를 위한 지연 시간
            if fps_control > 0:
                time.sleep(fps_control)
                
    st.success("✅ 3D 시뮬레이션 완료!")
else:
    st.info("좌측 사이드바의 버튼을 눌러 3D 시뮬레이션을 시작하세요.")
