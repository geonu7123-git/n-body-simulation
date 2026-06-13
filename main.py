import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="N-Body Simulation", layout="wide")
st.title("🌌 Universe Sandbox 스타일 N-Body 시뮬레이션")
st.write("Plotly 가속을 이용해 게임처럼 부드러운 천체 움직임을 구현합니다.")

# 2. 사이드바 - 파라미터 설정
st.sidebar.header("⚙️ 시뮬레이션 설정")
G = st.sidebar.number_input("중력 상수 (G)", value=1.0, step=0.1)
dt = st.sidebar.number_input("시간 간격 (dt)", value=0.01, step=0.001, format="%.3f")

# 프레임 수 (애니메이션의 총 길이)
num_frames = st.sidebar.slider("애니메이션 총 프레임 수", 100, 1000, 300, step=50)
num_bodies = st.sidebar.slider("천체 개수", 2, 8, 3)

# 3. 천체 초기값 설정 (무작위 생성)
np.random.seed(42)
masses = np.random.uniform(20, 150, num_bodies)
positions = np.random.uniform(-5, 5, (num_bodies, 2))
velocities = np.random.uniform(-2, 2, (num_bodies, 2))

# 정보 표시
st.subheader("🪐 천체 초기 상태")
cols = st.columns(num_bodies)
for i in range(num_bodies):
    with cols[i]:
        st.metric(label=f"천체 {i+1} 질량", value=f"{masses[i]:.1f}")

st.markdown("---")

# 4. 시뮬레이션 데이터 미리 계산 (물리 엔진 루프)
# 게임처럼 부드럽게 보이려면 실시간 재생 대신 데이터를 미리 물리 연산해두어야 합니다.
history_x = [positions[:, 0].copy()]
history_y = [positions[:, 1].copy()]

for frame in range(num_frames):
    forces = np.zeros((num_bodies, 2))
    for i in range(num_bodies):
        for j in range(num_bodies):
            if i != j:
                r_vec = positions[j] - positions[i]
                distance = np.linalg.norm(r_vec) + 0.2  # Softening 단위를 늘려 충돌 시 튕김 현상 완화
                force_mag = G * masses[i] * masses[j] / (distance**2)
                forces[i] += force_mag * (r_vec / distance)
                
    accelerations = forces / masses[:, np.newaxis]
    velocities += accelerations * dt
    positions += velocities * dt
    
    # 위치 기록 저장
    history_x.append(positions[:, 0].copy())
    history_y.append(positions[:, 1].copy())

history_x = np.array(history_x)
history_y = np.array(history_y)

# 5. Plotly 내장 애니메이션 엔진을 이용한 고속 렌더링
frames = []
for t in range(num_frames):
    frames.append(go.Frame(
        data=[go.Scatter(
            x=history_x[t],
            y=history_y[t],
            mode='markers',
            marker=dict(
                size=list(masses * 0.3 + 10), # 질량에 따른 크기
                color=list(range(num_bodies)), # 천체별 고유 색상
                colorscale='Viridis',
                line=dict(width=1, color='white')
            )
        )],
        name=str(t)
    ))

# 초기 그래프 프레임 설정
fig = go.Figure(
    data=[go.Scatter(
        x=history_x[0],
        y=history_y[0],
        mode='markers',
        marker=dict(
            size=list(masses * 0.3 + 10),
            color=list(range(num_bodies)),
            colorscale='Viridis',
            line=dict(width=1, color='white')
        )
    )],
    layout=go.Layout(
        xaxis=dict(range=[-15, 15], autoresize=False, zeroline=False, gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(range=[-15, 15], autoresize=False, zeroline=False, gridcolor='rgba(255,255,255,0.1)'),
        height=700,
        template="plotly_dark", # 유니버스 샌드박스 느낌의 다크 모드 우주 배경
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(label="▶ Play (재생)",
                     method="animate",
                     args=[None, dict(frame=dict(duration=15, redraw=False), fromcurrent=True, transition=dict(duration=0))]),
                dict(label="⏸ Pause (일시정지)",
                     method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))])
            ]
        )],
        sliders=[dict(
            steps=[dict(method="animate",
                        args=[[str(k)], dict(frame=dict(duration=0, redraw=False), mode="immediate", transition=dict(duration=0))],
                        label=str(k)) for k in range(num_frames)],
            transition=dict(duration=0),
            x=0, y=0, currentvalue=dict(font=dict(size=12), prefix="Frame: ", visible=True, xanchor="right")
        )]
    ),
    frames=frames
)

# 최종 그래프 출력
st.plotly_chart(fig, use_container_width=True)
