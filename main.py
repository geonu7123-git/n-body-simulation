import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# 1. 페이지 설정
st.set_page_config(page_title="Smooth N-Body Sim", layout="wide")

# 2. 사이드바 설정 (좌측 상단 제어)
with st.sidebar:
    st.title("🌌 시뮬레이션 설정")
    start_btn = st.button("🚀 시뮬레이션 시작", use_container_width=True)
    st.divider()
    G = st.slider("중력 상수 (G)", 0.1, 10.0, 2.0, 0.5)
    dt = st.slider("시간 간격 (dt)", 0.001, 0.05, 0.01, 0.001, format="%.3f")
    steps = st.slider("총 스텝 수", 100, 2000, 500, 100)
    
# 3. 물리 엔진 함수 (Velocity Verlet 알고리즘: Euler보다 훨씬 부드럽고 정확함)
def get_acc(pos, mass, G):
    N = pos.shape[0]
    acc = np.zeros_like(pos)
    for i in range(N):
        for j in range(N):
            if i != j:
                diff = pos[j] - pos[i]
                dist = np.linalg.norm(diff) + 0.1 # Softening (충돌 방지)
                acc[i] += G * mass[j] * diff / (dist**3)
    return acc

# 4. 메인 화면 구성
st.title("🪐 실시간 N-Body 물리 시뮬레이션")
st.caption("Velocity Verlet 통합 방식을 사용하여 궤도의 정밀도와 부드러움을 극대화했습니다.")

plot_spot = st.empty() # 애니메이션이 그려질 자리

# 5. 초기 조건 (태양-지구-달 시스템 모사)
pos = np.array([[0.0, 0.0], [2.5, 0.0], [-2.5, 0.0]])
vel = np.array([[0.0, 0.0], [0.0, 2.5], [0.0, -2.5]])
mass = np.array([20.0, 2.0, 2.0])

# 6. 버튼 클릭 시 실행
if start_btn:
    acc = get_acc(pos, mass, G) # 초기 가속도
    
    for step in range(steps):
        # Velocity Verlet: 1. 위치 업데이트
        pos = pos + vel * dt + 0.5 * acc * dt**2
        
        # Velocity Verlet: 2. 새로운 가속도 계산
        new_acc = get_acc(pos, mass, G)
        
        # Velocity Verlet: 3. 속도 업데이트
        vel = vel + 0.5 * (acc + new_acc) * dt
        acc = new_acc
        
        # 렌더링 성능 최적화: 3스텝마다 그리기 (더 부드러운 화면)
        if step % 3 == 0:
            fig, ax = plt.subplots(figsize=(7, 7), facecolor='#0e1117')
            ax.set_facecolor('#0e1117')
            
            # 행성 그리기
            colors = ['#FF4B4B', '#1C83E1', '#00C781']
            ax.scatter(pos[:, 0], pos[:, 1], s=mass*20, c=colors, edgecolors='white', alpha=0.8)
            
            # 스타일 설정
            ax.set_xlim(-8, 8)
            ax.set_ylim(-8, 8)
            ax.grid(color='gray', linestyle='--', alpha=0.3)
            ax.axis('off')
            ax.set_title(f"Step: {step} / {steps}", color='white', fontsize=12)
            
            plot_spot.pyplot(fig)
            plt.close(fig)
            
    st.success("✅ 시뮬레이션 완료!")
else:
    st.info("좌측 상단의 버튼을 눌러 시뮬레이션을 시작하세요.")
