import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="과제 대시보드")
# ✅ 기본 설정: 한글 폰트
plt.rcParams['font.family'] = 'Malgun Gothic'


@st.cache_data
def load_data():
    df = pd.read_csv("project_data.csv")
    진행률_map = {"O": 100, "△": 50, "X": 0}
    df["진행률"] = df["진행결과"].map(진행률_map)
    return df

df = load_data()

st.markdown("<h1 style='text-align:center;'>📊 정량 및 회의록 기반 과제 대시보드</h1>", unsafe_allow_html=True)
with st.sidebar:
    st.header("📅 공통 필터")
    selected_month = st.selectbox("월 선택", sorted(df["월"].unique()), key="shared_month")
    selected_dept = st.selectbox("부서 선택", ["전체"] + sorted(df["부서"].unique()), key="shared_dept")
    

tab1, tab2 = st.tabs(["월별 중점 과제 Dashboard", "회의록 기반 과제 현황"])
with tab1:
    filtered_df = df[df["월"] == selected_month]
    if selected_dept != "전체":
        filtered_df = filtered_df[filtered_df["부서"] == selected_dept]

    중요 = filtered_df[filtered_df["구분"] == "중요과제"]
    일반 = filtered_df[filtered_df["구분"] == "일반과제"]
    전체_평균 = filtered_df["진행률"].mean()
    중요_평균 = 중요["진행률"].mean()
    일반_평균 = 일반["진행률"].mean()

    def 결과별_갯수(df):
        return {"△": (df["진행결과"] == "△").sum(), "X": (df["진행결과"] == "X").sum()}

    중요_미달성 = 결과별_갯수(중요)
    일반_미달성 = 결과별_갯수(일반)

    # ▶ KPI 카드 스타일 요약
    st.markdown(f"<h3 style='margin-bottom: 0.5em;'>📌 {selected_month} 진행 현황 요약</h3>", unsafe_allow_html=True)
    
    with st.container():
        k1, k2, k3 = st.columns(3)
        k1.markdown(f"""
        <div style='background-color:#FFFFFF; border:1px solid #ccc; padding:15px; border-radius:10px; text-align:center;'>
            <b>전체 평균 진행률</b><br>
            <span style='font-size: 24px; color:#000;'>{전체_평균:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        k2.markdown(f"""
        <div style='background-color:#FFF3CD; border:2px solid #FFB74D; padding:15px; border-radius:10px; text-align:center;'>
            <b>중요과제 평균</b><br>
            <span style='font-size: 24px; color:#FF5733;'>{중요_평균:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
        
        k3.markdown(f"""
        <div style='background-color:#FFFFFF; border:1px solid #ccc; padding:15px; border-radius:10px; text-align:center;'>
            <b>일반과제 평균</b><br>
            <span style='font-size: 24px; color:#000;'>{일반_평균:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
    
    with st.container():
        m1, m2 = st.columns(2)
        m1.markdown(f"""
        <div style='background-color:#FCE4EC; border:2px solid #F48FB1; padding:12px; border-radius:10px; text-align:center;'>
            <b>중요 미달성</b><br>
            <span style='font-size: 20px;'>△ {중요_미달성['△']}건 / X {중요_미달성['X']}건</span>
        </div>
        """, unsafe_allow_html=True)
        
        m2.markdown(f"""
        <div style='background-color:#FFFFFF; border:1px solid #ccc; padding:12px; border-radius:10px; text-align:center;'>
            <b>일반 미달성</b><br>
            <span style='font-size: 20px;'>△ {일반_미달성['△']}건 / X {일반_미달성['X']}건</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    # ▶ 부서별 평균 진행률 시각화
    st.markdown("### 🏢 부서별 평균 진행률")
    col6, col7 = st.columns(2)
    for df_sub, title, col in zip([중요, 일반], ["중요과제", "일반과제"], [col6, col7]):
        부서별 = df_sub.groupby("부서")["진행률"].mean().reset_index()
        fig = px.bar(
            부서별,
            x="진행률",
            y="부서",
            orientation="h",
            color="부서",
            text="진행률",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(
            marker_line_width=0,
            marker_line_color="gray",
            texttemplate="%{text:.1f}%",
            textposition="inside",
            textfont_color="white",
            width=0.5
        )
        fig.update_layout(
            title=f"{title} 평균 진행률",
            title_font_size=16,
            margin=dict(l=10, r=10, t=40, b=10),
            height=350,
            bargap=0.3,
            showlegend=False,
            xaxis=dict(showticklabels=False, range=[0, 100]),
            yaxis_title=None,
            xaxis_title=None,
        )
        col.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # ▶ 부서별 미달성 과제 현황
    st.markdown("### ❗ 부서별 미달성 과제 현황 (△ / X 구분)")
    col1, col2 = st.columns(2)
    for gubun, col, show_legend in zip(
            ["중요과제", "일반과제"],
            [col1, col2],
            [False, True]
    ):
        sub_df = filtered_df[(filtered_df["구분"] == gubun)]
        부서_list = sub_df["부서"].unique()
        진행결과_list = ["△", "X"]
        
        sub_df = filtered_df[filtered_df["구분"] == gubun]
        부서_list = sub_df["부서"].unique()
        
        미달성_df = sub_df[sub_df["진행결과"].isin(["△", "X"])]
        
        # 2. groupby 후 부서 기준 누락 보완
        count_df = 미달성_df.groupby(["부서", "진행결과"]).size().unstack().fillna(0)
        
        for dept in 부서_list:
            if dept not in count_df.index:
                count_df.loc[dept] = {"△": 0, "X": 0}
        
        count_df = count_df.reset_index()
        
        # # ✅ 디버깅용 출력 (조건 체크 전)
        # st.write(f"--- {gubun} ---")
        # st.write("count_df")
        # st.dataframe(count_df)
        # st.write("부서 목록:", 부서_list)
        #
        cols = count_df.columns if not count_df.empty else []
        condition_result = all(col not in cols or count_df[col].sum() == 0 for col in ["△", "X"])
        #
        # # ✅ 조건 진입 여부 확인
        # st.write("조건 결과 (미달성 없음인가?):", condition_result)
        #
        if condition_result:
            tick_vals = list(부서_list)
            
            # y=0.01짜리 바 만들기 (눈에는 거의 안 보임)
            trace_dummy = go.Bar(
                x=tick_vals,
                y=[0.01] * len(tick_vals),
                marker_color='rgba(0,0,0,0.001)',  # 완전 투명은 일부 환경에서 생략됨 → 0.001로 처리
                hoverinfo='skip',
                showlegend=False,
                name="invisible"
            )
            
            # 그래프 생성
            fig = go.Figure(data=[trace_dummy])
            fig.update_layout(
                title=f"{gubun} (미달성 없음)",
                barmode="stack",
                height=350,
                margin=dict(t=40, b=10, l=10, r=10),
                xaxis=dict(
                    title=None,
                    tickmode="array",
                    tickvals=tick_vals,
                    ticktext=tick_vals,
                ),
                yaxis=dict(title=None, range=[0, 1]),
                showlegend=False
            )
            
            # 그래프 출력
            col.plotly_chart(fig, use_container_width=True)
        
        else:
            existing_cols = [col for col in ["△", "X"] if col in count_df.columns]
            
            melted = count_df.melt(
                id_vars="부서",
                value_vars=existing_cols,
                var_name="진행결과",
                value_name="건수"
            )
            fig = px.bar(
                melted,
                x="부서",
                y="건수",
                color="진행결과",
                barmode="stack",
                text="건수",
                color_discrete_map={"△": "#F9CB40", "X": "#E76F51"},
                title=f"{gubun}"
            )
            fig.update_traces(
                textposition="inside",
                marker_line_width=0.0,
                marker_line_color="gray",
                width=0.3
            )
            부서_순서_리스트 = sorted(부서_list)
            fig.update_layout(
                xaxis=dict(
                    categoryorder='array',
                    categoryarray=부서_순서_리스트,
                    title=None
                ),
                height=350,
                margin=dict(t=40, b=10, l=10, r=10),
                showlegend=show_legend,
                xaxis_title=None,
                yaxis_title=None,
            )
            col.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")

    # ▶ 미달성 과제 상세 목록
    st.markdown("### 📋 미달성 과제 상세 목록")
    미달성_과제표 = filtered_df[filtered_df["진행률"] < 100][
        ["구분", "부서", "팀", "담당자", "과제명", "월별목표", "월별실적", "진행결과", "코멘트"]
    ]
    st.dataframe(미달성_과제표.reset_index(drop=True), use_container_width=True, height=350)


# ▶ 회의록 기반 탭
with tab2:
    st.header("회의록 기반 과제 상태(LLM 요약)")

    try:
        llm_df = pd.read_csv("report_llm.csv")

        # 📌 사이드바에서 선택한 필터 적용
        selected_month = st.session_state.get("shared_month", "전체")
        selected_dept = st.session_state.get("shared_dept", "전체")

        # ✅ tab2 전용 "전체 월 보기" 체크박스
        show_all_months = st.checkbox("🗓️ 전체 월 보기", value=False)
        
        # ✅ 부서 먼저 필터링해서 해당 부서 과제만 표시
        task_pool_df = llm_df.copy()
        if selected_dept != "전체":
            task_pool_df = task_pool_df[task_pool_df["부서"] == selected_dept]
        전체_과제 = sorted(task_pool_df["과제명"].dropna().unique())

        selected_tasks = st.multiselect(
            "📌 세부 과제 선택 (복수 선택 가능)", 전체_과제, default=[], key="llm_tasks"
        )
 
        # ✅ 조건별 필터링
        filtered_llm = llm_df.copy()
        if not show_all_months and selected_month != "전체":
            filtered_llm = filtered_llm[filtered_llm["월"] == selected_month]
        if selected_dept != "전체":
            filtered_llm = filtered_llm[filtered_llm["부서"] == selected_dept]
        if selected_tasks:
            filtered_llm = filtered_llm[filtered_llm["과제명"].isin(selected_tasks)]
        
        # ✅ 상태별 카드 표시
        if not filtered_llm.empty:
            st.markdown("### 📌 과제 상태별 회의 요약")
            status_group = filtered_llm.groupby("Status")

            for status, group in status_group:
                st.markdown(f"#### {'✅' if status=='On-track' else '⚠️' if status=='Risk' else '⏳'} {status} ({len(group)}건)")
                for _, row in group.iterrows():
                    액션텍스트 = ""
                    if isinstance(row["액션 아이템"], str) and row["액션 아이템"].strip():
                        액션텍스트 = f"<br><b>액션:</b> <i>{row['액션 아이템']}</i>"
                    
                    st.markdown(f"""
                            <div style="border:1px solid #ddd; border-radius:8px; padding:12px; margin-bottom:10px; background-color:#FAFAFA">
                                <b>{row['과제명']}</b> <span style="font-size:13px; color:#888;">({row['회의일']} · {row['팀']})</span>
                                <br><span style="font-size: 13px; color:#444;">📝 {row['회의 요약']}</span>
                                {액션텍스트}
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("조건에 맞는 회의록 데이터가 없습니다.")

        # 📂 전체 테이블 (숨김)
        with st.expander("📄 전체 회의 요약 테이블 보기"):
            st.dataframe(filtered_llm, use_container_width=True, height=400)

    except FileNotFoundError:
        st.warning("❗ report_llm.csv 파일이 없습니다. 파일 업로드 후 확인해주세요.")
