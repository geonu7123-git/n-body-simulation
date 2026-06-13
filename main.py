import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="N-Body Simulation", layout="wide")
st.title("🌌 N-Body 천체 시뮬레이션")
st.write("중력 상호작용에 따른 천체들의 움직임을 시뮬레이션합니다.")

# 2. 사이드바 - 파라미터 설정
st.sidebar.header("⚙️ 시뮬레이션 설정")
G = st.sidebar.number_input("중력 상수 (G)", value=1.0, step=0.1)
dt = st.sidebar.number_input("시간 간격 (dt)", value=0.01, step=0.001, format="%.3f")

# [수정] 스텝 수 대신 '프레임 수'로 대체
num_frames = st.sidebar.slider("애니메이션 프레임 수", 50, 500, 200)
num_bodies = st.sidebar.slider("천체 개수", 2, 5, 3)

# 3. 천체 초기값 설정 (무작위 생성)
np.random.seed(42)  # 일관된 결과를 위한 시드 고정
masses = np.random.uniform(10, 100, num_bodies)
positions = np.random.uniform(-5, 5, (num_bodies, 2))
velocities = np.random.uniform(-1, 1, (num_bodies, 2))

# 정보 표시
st.subheader("🪐 천체 초기 상태")
for i in range(num_bodies):
    st.write(f"**천체 {i+1}** | 질량: {masses[i]:.2f} | 위치: ({positions[i,0]:.2f}, {positions[i,1]:.2f}) | 속도: ({velocities[i,0]:.2f}, {velocities[i,1]:.2f})")

st.markdown("---")

# 4. 애니메이션을 위한 그래프 출력 공간 준비
plot_spot = st.empty()
start_btn = st.sidebar.button("🚀 시뮬레이션 시작")

# 5. 시뮬레이션 실행 제어 (들여쓰기 유지)
if start_btn:
    st.sidebar.success("시뮬레이션 진행 중...")
    
    # 위치 기록을 위한 리스트
    history = [positions.copy()]
    
    # [수정] num_steps 대신 num_frames 만큼 루프 작동
    for frame in range(num_frames):
        forces = np.zeros((num_bodies, 2))
        
        # 모든 천체 간의 중력 계산
        for i in range(num_bodies):
            for j in range(num_bodies):
                if i != j:
                    r_vec = positions[j] - positions[i]
                    distance = np.linalg.norm(r_vec) + 1e-4  # 충돌로 인한 분모 0 방지 (Softening)
                    force_mag = G * masses[i] * masses[j] / (distance**2)
                    forces[i] += force_mag * (r_vec / distance)
        
        # 가속도, 속도, 위치 업데이트
        accelerations = forces / masses[:, np.newaxis]
        velocities += accelerations * dt
        positions += velocities * dt
        
        # 실시간 시각화 (matplotlib 이용)
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(-10, 10)
        ax.set_ylim(-10, 10)
        # [수정] 상단 타이틀 표기도 Frame으로 변경
        ax.set_title(f"Animation Frame: {frame + 1}/{num_frames}")
        ax.grid(True, linestyle='--', alpha=0.5)
        
        # 천체 위치 그리기
        for i in range(num_bodies):
            ax.scatter(positions[i, 0], positions[i, 1], s=masses[i]*3, label=f"Body {i+1}")
            
        ax.legend(loc="upper right")
        
        # Streamlit 화면에 그래프 업데이트
        plot_spot.pyplot(fig)
        plt.close(fig)  # 메모리 확보를 위해 종료
        
        # 시뮬레이션 속도 조절
        time.sleep(0.02)
        
    st.sidebar.info("시뮬레이션이 완료되었습니다!")
