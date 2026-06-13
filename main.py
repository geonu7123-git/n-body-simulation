import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="N-Body Simulation", layout="centered")
st.title("🌌 간소화된 N-Body 시뮬레이션")
st.sidebar.header("🔧 시뮬레이션 설정")

# 2. 사이드바 인터랙티브 제어 요소
G = st.sidebar.slider("중력 상수 (G)", 0.1, 5.0, 1.0, 0.1)
dt = st.sidebar.slider("시간 간격 (dt)", 0.01, 0.1, 0.05, 0.01)
steps = st.sidebar.slider("시뮬레이션 스텝 수", 50, 300, 150, 10)

# 3. 초기 데이터 설정 (N=3, 3체 문제 예시)
# 위치(x, y), 속도(vx, vy), 질량(m)
pos = np.array([[0.0, 0.0], [2.0, 0.0], [-2.0, 0.0]])
vel = np.array([[0.0, 0.0], [0.0, 0.5], [0.0, -0.5]])
mass = np.array([10.0, 1.0, 1.0])

# 4. 실시간 애니메이션을 위한 Streamlit 빈 그래픽 플레이스홀더
plot_spot = st.empty()

# 5. 시뮬레이션 루프
for step in range(steps):
    # 각 입자에 작용하는 가속도 초기화 (N, 2)
    acc = np.zeros_like(pos)
    
    # 만유인력 법칙 계산 (F = G * m1 * m2 / r^2)
    for i in range(len(pos)):
        for j in range(len(pos)):
            if i != j:
                diff = pos[j] - pos[i]
                dist = np.linalg.norm(diff) + 1e-3  # 0으로 나누기 방지(Softening)
                acc[i] += G * mass[j] * diff / (dist**3)
    
    # 속도 및 위치 업데이트 (오일러 방법)
    vel += acc * dt
    pos += vel * dt
    
    # Matplotlib을 이용한 시각화 생성
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(pos[:, 0], pos[:, 1], s=mass*10, c=['red', 'blue', 'green'])
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_title(f"Simulation Step: {step + 1}")
    ax.grid(True)
    
    # Streamlit 화면에 업데이트
    plot_spot.pyplot(fig)
    plt.close(fig)  # 메모리 확보를 위해 플롯 닫기

st.success("시뮬레이션이 완료되었습니다!")
