import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# 1. 페이지 설정
st.set_page_config(page_title="3D N-Body Sim", layout="wide")

# 2. 세션 상태 초기화 (무한 루프 제어용)
if "running" not in st.session_state:
    st.session_state.running = False

# 3. 사이드바 설정 (Step 삭제, FPS 제어 추가)
with st.sidebar:
    st.title("🌌 3D 시뮬레이션 설정")
    
    # 시작 / 중지 제어 버튼
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 시작", use_container_width=True):
            st.session_state.running = True
    with col2:
        if st.button("🛑 중지", use_container_width=True):
            st.session_state.running = False
            
    st.divider()
    G = st.slider("중력 상수 (G)", 0.1, 10.0, 2.0, 0.5)
    dt = st.slider("시간 간격 (dt)", 0.001, 0.05, 0.01, 0.001, format="%.3f")
    
    st.divider()
    st.subheader("⏱️ 화면 재생 설정")
    # 사용자가 직관적으로 초당 프레임 수(FPS)를 조절하도록 변경
    target_fps = st.slider("목표 프레임 수 (FPS)", 5, 60, 30, 5)
    render_ratio = st.slider("물리 계산 정밀도 (프레임당 연산 횟수)", 1, 10, 2)

# FPS를 지연 시간(초)으로 변환
frame_delay = 1.0 / target_fps

# 4. 3D 물리 엔진 함수 (Velocity Verlet)
def get_acc_3d(pos, mass, G):
    N = pos.shape[0]
    acc = np.zeros_like(pos)
    for i in range(N):
        for j in range(N):
            if i != j:
                diff = pos[j] - pos[i]
                dist = np.linalg.norm(diff) + 0.1 # Softening
                acc[i] += G * mass[j] * diff / (dist**3)
    return acc

# 5. 메인 화면 구성
st.title("🪐 실시간 3D N-Body 물리 시뮬레이션")
st.caption("오류가 수정되었으며, 이제 스텝 제한 없이 설정한 FPS에 맞춰 무한히 부드럽게 구동됩니다.")

plot_spot = st.empty()

# 6. 초기 조건 설정 (X, Y, Z)
# 앱이 재실행되어도 위치가 초기화되지 않도록 session_state에 저장 가능하지만, 
# 여기서는 시작 버튼 누를 때마다 초기화되도록 구성했습니다.
pos = np.array([
    [0.0, 0.0, 0.0],    # 중앙 천체
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

# 7. 무한 루프 구동 (st.session_state.running이 True인 동안 지속)
if st.session_state.running:
    acc = get_acc_3d(pos, mass, G)
    step_counter = 0
    
    while st.session_state.running:
        start_time = time.time()
        
        # 지정된 물리 계산 정밀도만큼 내부 연산 반복 (화면은 한 번만 그림)
        for _ in range(render_ratio):
            pos = pos + vel * dt + 0.5 * acc * dt**2
            new_acc = get_acc_3d(pos, mass, G)
            vel = vel + 0.5 * (acc + new_acc) * dt
            acc = new_acc
            step_counter += 1
        
        # 3D 차트 생성 및 에러 수정 부분
        fig = go.Figure()
        for i in range(len(pos)):
            fig.add_trace(go.Scatter3d(
                # 💡 수정 완료: 복잡한 문법을 제거하고 좌표값만 깔끔하게 리스트로 매핑
                x=[pos[i, 0]], 
                y=[pos[i, 1]], 
                z=[pos[i, 2]], 
                mode='markers',
                name=names[i],
                marker=dict(
                    size=mass[i] * 0.8 + 5,
                    color=colors[i],
                    opacity=0.9,
                    line=dict(color='white', width=1)
                )
            ))
        
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=0, r=0, b=0, t=40),
            scene=dict(
                xaxis=dict(range=[-8, 8], backgroundcolor="rgba(0,0,0,0)", gridcolor="gray", showbackground=True),
                yaxis=dict(range=[-8, 8], backgroundcolor="rgba(0,0,0,0)", gridcolor="gray", showbackground=True),
                zaxis=dict(range=[-8, 8], backgroundcolor="rgba(0,0,0,0)", gridcolor="gray", showbackground=True),
                aspectmode='cube'
            ),
            title=dict(text=f"📊 총 연산 횟수: {step_counter} step (실시간 무한 구동 중)", x=0.5, y=0.95),
            height=650
        )
        
        plot_spot.plotly_chart(fig, use_container_width=True)
        
        # ⏱️ 설정한 FPS 속도를 유지하기 위한 동적 지연 시간 계산
        elapsed_time = time.time() - start_time
        sleep_time = max(0.0, frame_delay - elapsed_time)
        if sleep_time > 0:
            time.sleep(sleep_time)
            
        # Streamlit이 중지 버튼 이벤트를 감지할 수 있도록 미세한 틈을 줌
        st.rerun()

else:
    st.info("좌측 사이드바의 🚀 시작 버튼을 누르면 시뮬레이션이 무한히 진행됩니다. 🛑 중지 버튼으로 언제든 멈출 수 있습니다.")
