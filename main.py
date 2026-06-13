import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="Fine N-Body Simulation", layout="centered")
st.title("🌌 정밀한 N-Body 시뮬레이션")
st.sidebar.header("🔧 시뮬레이션 설정")

# 2. 사이드바 인터랙티브 제어 요소 (시간 간격을 더 세밀하게 조절 가능하도록 수정)
G = st.sidebar.slider("중력 상수 (G)", 0.1, 5.0, 1.0, 0.1)
# dt의 최소값을 0.001로 줄이고, 기본값을 0.01로 더 촘촘하게 설정했습니다.
dt = st.sidebar.slider("시간 간격 (dt)", 0.001, 0.05, 0.01, 0.001, format="%.3f")
# 시간 간격이 줄어든 만큼 더 오래 관찰할 수 있도록 스텝 수 최대치를 1000으로 늘렸습니다.
steps = st.sidebar.slider("시뮬레이션 스텝 수", 50, 1000, 300, 50)

# 3. 초기 데이터 설정 (N=3, 3체 문제 예시)
pos = np.array([[0.0, 0.0], [2.0, 0.0], [-2.0, 0.0]])
vel = np.array([[0.0, 0.0], [0.0, 0.5], [0.0, -0.5]])
mass = np.array([10.0, 1.0, 1.0])

# 4. 실시간 애니메이션을 위한 Streamlit 빈 그래픽 플레이스홀더
plot_spot = st.empty()

# 5. 시뮬레이션 루프
for step in range(steps):
    acc = np.zeros_like(pos)
    
    # 만유인력 법칙 계산
    for i in range(len(pos)):
        for j in range(len(pos)):
            if i != j:
                diff = pos[j] - pos[i]
                dist = np.linalg.norm(diff) + 1e-3  # Softening
                acc[i] += G * mass[j] * diff / (dist**3)
    
    # 속도 및 위치 업데이트 (줄어든 dt 적용)
    vel += acc * dt
    pos += vel * dt
    
    # 매 스텝마다 그리거나, 너무 느려지면 일정 스텝마다 그리도록 설정 가능
    # 여기서는 매 스텝 실시간 업데이트합니다.
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(pos[:, 0], pos[:, 1], s=mass*10, c=['red', 'blue', 'green'])
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_title(f"Simulation Step: {step + 1} (dt: {dt})")
    ax.grid(True)
    
    # Streamlit 화면에 업데이트
    plot_spot.pyplot(fig)
    plt.close(fig)

st.success("시뮬레이션이 완료되었습니다!")
