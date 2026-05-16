"""
RecruitIQ — AI Resume Analyzer & Recruiter Search System
Frontend only. Place at: frontend/streamlit_app.py
Run: streamlit run frontend/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time
import sys
import os
import tempfile
import uuid
from reportlab.platypus import *
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from ai_engine.parser.resume_parser import (
    extract_text_from_pdf
)

from ai_engine.ats.ats_score import (
    calculate_ats_score
)

from ai_engine.embeddings.semantic_matcher import (
    calculate_semantic_similarity
)

from ai_engine.recommendations.recommender import (
    generate_recommendations
)

from database.chroma_store import (
    store_resume,
    search_resumes
)

from utils.report_generator import (
    generate_report
)

# ── Must be first Streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title="RecruitIQ · AI Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
  --bg:     #080c14; --card: rgba(255,255,255,.04); --border: rgba(255,255,255,.09);
  --cyan:   #00e5ff; --violet: #7c3aed; --green: #00ffa3;
  --amber:  #ffb300; --rose: #ff4d7d;
  --t1: #f0f4ff;     --t2: #8b9fc9;    --t3: #4b5a7a;
}

html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  font-family: 'DM Sans', sans-serif !important;
  color: var(--t1) !important;
}
#MainMenu, footer, header,
[data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }

[data-testid="stSidebar"] { background: #0a0f1c !important; border-right: 1px solid var(--border) !important; }
[data-testid="stSidebar"] * { color: var(--t1) !important; }

.stButton > button {
  background: linear-gradient(135deg, var(--violet), #4f46e5) !important;
  color: #fff !important; border: none !important; border-radius: 10px !important;
  font-weight: 600 !important; font-family: 'DM Sans', sans-serif !important;
  padding: .5rem 1.4rem !important; box-shadow: 0 4px 16px rgba(124,58,237,.4) !important;
  transition: all .25s ease !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(124,58,237,.55) !important; }

.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
  background: rgba(255,255,255,.04) !important; border: 1px solid var(--border) !important;
  border-radius: 10px !important; color: var(--t1) !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
  border-color: var(--cyan) !important; box-shadow: 0 0 0 3px rgba(0,229,255,.12) !important;
}

[data-testid="stFileUploader"] {
  border: 2px dashed rgba(0,229,255,.25) !important; border-radius: 14px !important;
  background: rgba(0,229,255,.03) !important; padding: 1rem !important; transition: all .25s !important;
}
[data-testid="stFileUploader"]:hover { border-color: rgba(0,229,255,.5) !important; }

.stProgress > div > div > div > div {
  background: linear-gradient(90deg, var(--cyan), var(--violet)) !important; border-radius: 99px !important;
}

[data-testid="stMetric"] {
  background: var(--card) !important; border: 1px solid var(--border) !important;
  border-radius: 14px !important; padding: 1rem 1.2rem !important; transition: all .25s !important;
}
[data-testid="stMetric"]:hover { background: rgba(255,255,255,.07) !important; }
[data-testid="stMetricLabel"] { color: var(--t2) !important; font-size: .75rem !important; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; }

[data-testid="stTabs"] [data-baseweb="tab"] { background: transparent !important; color: var(--t2) !important; font-family: 'DM Sans', sans-serif !important; }
[data-testid="stTabs"] [aria-selected="true"] { color: var(--cyan) !important; border-bottom: 2px solid var(--cyan) !important; }

hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,.1); border-radius: 99px; }

/* Reusable components */
.card {
  background: var(--card); border: 1px solid var(--border); border-radius: 14px;
  padding: 1.3rem; margin-bottom: .5rem; transition: all .25s;
}
.card:hover { background: rgba(255,255,255,.07); border-color: rgba(255,255,255,.16); transform: translateY(-1px); }

.tag {
  display: inline-block; padding: .25rem .7rem; border-radius: 99px;
  font-size: .72rem; font-weight: 500; margin: .15rem;
}
.tag-green  { background: rgba(0,255,163,.12);  color: #00ffa3; border: 1px solid rgba(0,255,163,.25); }
.tag-rose   { background: rgba(255,77,125,.12); color: #ff4d7d; border: 1px solid rgba(255,77,125,.25); }
.tag-cyan   { background: rgba(0,229,255,.12);  color: #00e5ff; border: 1px solid rgba(0,229,255,.25); }
.tag-violet { background: rgba(124,58,237,.15); color: #c4b5fd; border: 1px solid rgba(124,58,237,.3); }

.sh { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; color: var(--t1); margin: 0 0 1rem; }
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; margin-right: .4rem; }
 .dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; margin-right: .4rem; }

/* Layout Fixes */
.main .block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 0.5rem !important;
    padding-left: 1.2rem !important;
    padding-right: 1.2rem !important;
    max-width: 100% !important;
}

section.main > div {
    padding-top: 0rem !important;
}

[data-testid="stMetric"] {
    padding: .7rem .9rem !important;
}

.card {
    padding: 1rem !important;
    margin-bottom: .35rem !important;
}

[data-testid="stSidebar"] {
    min-width: 240px !important;
    max-width: 240px !important;
}

html, body, [data-testid="stAppViewContainer"] {
    overflow-x: hidden !important;
}


            
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def score_color(s):
    return "#00ffa3" if s >= 80 else "#00e5ff" if s >= 60 else "#ffb300" if s >= 40 else "#ff4d7d"

def score_label(s):
    return "Excellent" if s >= 80 else "Good" if s >= 60 else "Fair" if s >= 40 else "Poor"

def sh(icon, title, color="#00e5ff"):
    """Render a styled section header."""
    st.markdown(
        f'<div class="sh"><span class="dot" style="background:{color};box-shadow:0 0 6px {color}88;"></span>'
        f'{icon} {title}</div>', unsafe_allow_html=True)

def card(html):
    st.markdown(f'<div class="card">{html}</div>', unsafe_allow_html=True)

def tags_html(items, cls):
    return "".join(f'<span class="tag {cls}">{i}</span>' for i in items)

def score_card(label, score):
    c = score_color(score)
    card(f"""
      <div style="text-align:center;padding:.4rem 0;">
        <div style="font-family:'Syne',sans-serif;font-size:2.4rem;font-weight:800;
                    color:{c};text-shadow:0 0 16px {c}44;line-height:1;">
          {score:.0f}<span style="font-size:1rem;color:var(--t3);">%</span>
        </div>
        <div style="font-size:.67rem;letter-spacing:.07em;text-transform:uppercase;color:{c};font-weight:600;margin:.2rem 0;">
          {score_label(score)}</div>
        <div style="font-family:'Syne',sans-serif;font-size:.85rem;font-weight:700;">{label}</div>
        <div style="height:4px;background:rgba(255,255,255,.06);border-radius:99px;margin-top:.7rem;overflow:hidden;">
          <div style="height:100%;width:{score}%;background:{c};border-radius:99px;"></div>
        </div>
      </div>""")

# Matplotlib dark theme (set once globally)
plt.rcParams.update({
    "figure.facecolor":"#080c14", "axes.facecolor":"#0f1525",
    "axes.edgecolor":"#1a2240",   "axes.labelcolor":"#8b9fc9",
    "axes.titlecolor":"#f0f4ff",  "xtick.color":"#8b9fc9",
    "ytick.color":"#8b9fc9",      "grid.color":"#1a2240",
    "text.color":"#f0f4ff",       "grid.linewidth":.6,
})


# ── Session state ─────────────────────────────────────────────────────────────
for k, v in {"done":False,"ats":0.,"sem":0.,"matched":[],"missing":[],"recs":[],"candidates":[],"search_results":[]}.items():
    st.session_state.setdefault(k, v)


# ── Static demo data (swap with your backend calls) ───────────────────────────


DEMO_RECS = [
    {"p":"high",  "title":"Add Cloud ML Experience",  "body":"Include AWS SageMaker or Azure ML projects. The JD requires cloud deployment experience."},
    {"p":"high",  "title":"Quantify Achievements",    "body":"Replace vague statements with metrics. E.g. 'Reduced inference latency by 40%'."},
    {"p":"med",   "title":"Add MLOps & CI/CD",        "body":"Mention model versioning tools such as MLflow, DVC, or Weights & Biases."},
    {"p":"low",   "title":"Tailor Summary Section",   "body":"Mirror 2–3 key phrases from the JD to boost ATS lexical match score."},
]


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:.5rem 0 1.5rem;border-bottom:1px solid var(--border);margin-bottom:1.5rem;">
      <div style="display:flex;align-items:center;gap:.6rem;">
        <div style="width:34px;height:34px;background:linear-gradient(135deg,#00e5ff,#7c3aed);
                    border-radius:9px;display:flex;align-items:center;justify-content:center;
                    font-family:'Syne',sans-serif;font-weight:800;color:#fff;font-size:1rem;">R</div>
        <div>
          <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:800;">RecruitIQ</div>
          <div style="font-size:.62rem;color:var(--t3);">AI Platform · v2.0</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio("Navigate",
                    ["Dashboard","Resume Analyzer","Recruiter Search","Rankings","Analytics"],
                    label_visibility="collapsed")
    st.divider()
    min_score = st.slider("Min Score Filter", 0, 100, 60, format="%d%%")
    top_n     = st.selectbox("Top N Candidates", [5, 10, 15, 20], index=1)
    st.divider()
    st.markdown('<div style="font-size:.72rem;color:var(--t3);line-height:1.9;">'
                '● ChromaDB Connected<br>● MiniLM-L6-v2 Active<br>● ATS Engine v2</div>',
                unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
if page == "Dashboard":

    st.markdown("""
    <div style="background:linear-gradient(135deg,rgba(124,58,237,.18),rgba(0,229,255,.07),transparent);
                border:1px solid rgba(124,58,237,.3);border-radius:20px;padding:2.5rem 2rem;margin-bottom:2rem;">
      <div style="display:inline-block;background:rgba(0,229,255,.1);border:1px solid rgba(0,229,255,.25);
                  border-radius:99px;padding:.2rem .9rem;font-size:.7rem;font-weight:600;
                  color:#00e5ff;letter-spacing:.08em;margin-bottom:.8rem;">⚡ AI-POWERED RECRUITING</div>
      <h1 style="font-family:'Syne',sans-serif;font-size:2.3rem;font-weight:800;margin:0 0 .6rem;line-height:1.1;">
        Smarter Hiring,<br>
        <span style="background:linear-gradient(90deg,#00e5ff,#7c3aed);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">Powered by AI</span>
      </h1>
      <p style="color:var(--t2);font-size:.95rem;max-width:500px;line-height:1.65;margin:0;">
        ATS scoring · Semantic matching · Recruiter search · Candidate analytics — all in one platform.
      </p>
    </div>
    """, unsafe_allow_html=True)

    sh("📊", "Platform Overview", "#7c3aed")
    c1, c2, c3, c4 = st.columns(4)
    for col, label in zip([c1,c2,c3,c4], ["Resumes Analyzed","Avg ATS Score","Top Semantic Match","Indexed Profiles"]):
        col.metric(label, "—")

    st.markdown("<br>", unsafe_allow_html=True)
    sh("🚀", "Core Capabilities", "#00e5ff")

    features = [
        ("🧠","ATS Intelligence",    "Keyword extraction, format scoring, and section completeness calibrated to ATS gating logic."),
        ("🔗","Semantic Matching",   "MiniLM-L6-v2 embeddings in ChromaDB for deep similarity beyond keyword overlap."),
        ("📋","AI Recommendations", "Prioritised action items bridging the gap between your resume and the JD."),
    ]
    for col, (icon, title, desc) in zip(st.columns(3), features):
        with col:
            card(f'<div style="font-size:1.5rem;margin-bottom:.6rem;">{icon}</div>'
                 f'<div style="font-family:\'Syne\',sans-serif;font-size:.9rem;font-weight:700;margin-bottom:.35rem;">{title}</div>'
                 f'<div style="font-size:.75rem;color:var(--t2);line-height:1.6;">{desc}</div>')

    st.info("👈 Select **Resume Analyzer** in the sidebar to get started.", icon="💡")


# ═══════════════════════════════════════════════════════════════════════════════
# RESUME ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Resume Analyzer":

    sh("📄", "Resume Analyzer", "#00e5ff")

    col_up, col_jd = st.columns(2, gap="large")
    with col_up:
        st.markdown("**📎 Upload Resume (PDF)**")
        resume_file = st.file_uploader("PDF Resume", type=["pdf"], label_visibility="collapsed")

    with col_jd:
        st.markdown("**🎯 Job Description**")
        job_role = st.text_input("Job Title", placeholder="e.g. Senior Data Scientist")
        job_desc = st.text_area("Paste Job Description", placeholder="Paste the full JD here...", height=140)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("⚡ Analyze Resume"):
        if not resume_file:
            st.warning("Please upload a PDF resume.")
        elif not job_desc.strip():
            st.warning("Please paste a job description.")
        else:
            bar = st.progress(0)
            steps = ["Parsing PDF…","ATS scoring…","Generating embeddings…","Semantic matching…","Building recommendations…"]
            for i, msg in enumerate(steps):
                st.toast(msg, icon="⚙️"); time.sleep(0.3); bar.progress((i+1)*20)

            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(resume_file.read())
                pdf_path = tmp_file.name

                resume_text = extract_text_from_pdf(pdf_path)

                resume_id = str(uuid.uuid4())

                store_resume(resume_id, resume_text)

                ats_score, matched_skills, missing_skills = calculate_ats_score(resume_text, job_desc)

                semantic_score = calculate_semantic_similarity(resume_text, job_desc)

                recommendations = generate_recommendations(missing_skills)
                generate_report(

    ats_score,

    semantic_score,

    matched_skills,

    missing_skills,

    recommendations
)

                formatted_recommendations = []
                for rec in recommendations:
                    formatted_recommendations.append({"p":"med","title":rec,"body":rec})

                st.session_state.update({
                    "done": True,
                    "ats": ats_score,
                    "sem": semantic_score,
                    "matched": matched_skills,
                    "missing": missing_skills,
                    "recs": formatted_recommendations
                })
                bar.progress(100)
                time.sleep(0.1)
                bar.empty()
                st.success("✅ Analysis complete!")
                st.rerun()

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.done:
            ats, sem = st.session_state.ats, st.session_state.sem
            combined = round(ats*.5 + sem*.5, 1)

            st.markdown("<br>", unsafe_allow_html=True)
            sh("🎯", "Scores", "#00ffa3")
            for col, label, score in zip(st.columns(3), ["ATS Score","Semantic Match","Combined"], [ats,sem,combined]):
                with col: score_card(label, score)

            st.markdown("<br>", unsafe_allow_html=True)
            col_m, col_x = st.columns(2, gap="large")
            with col_m:
                sh("✅", "Matched Skills", "#00ffa3")
                card(f'<div style="font-size:.72rem;color:var(--t3);margin-bottom:.5rem;">{len(st.session_state.matched)} skills found</div>'
                    + tags_html(st.session_state.matched, "tag-green"))
            with col_x:
                sh("❌", "Missing Skills", "#ff4d7d")
                card(f'<div style="font-size:.72rem;color:var(--t3);margin-bottom:.5rem;">{len(st.session_state.missing)} skill gaps</div>'
                    + tags_html(st.session_state.missing, "tag-rose"))

            st.markdown("<br>", unsafe_allow_html=True)
            sh("🤖", "AI Recommendations", "#7c3aed")
            p_style = {"high":("#ff4d7d","HIGH"), "med":("#ffb300","MED"), "low":("#00ffa3","LOW")}
            for rec in st.session_state.recs:
                color, badge = p_style.get(rec["p"], ("#8b9fc9","—"))
                st.markdown(f"""
                <div class="card" style="border-left:3px solid {color};padding-left:1.2rem;">
                <div style="display:flex;align-items:center;gap:.45rem;margin-bottom:.2rem;">
                    <span style="font-size:.85rem;font-weight:600;">{rec['title']}</span>
                    <span style="font-size:.6rem;font-weight:700;color:{color};background:{color}18;
                                border:1px solid {color}33;padding:.1rem .5rem;border-radius:99px;">{badge}</span>
                </div>
                <div style="font-size:.76rem;color:var(--t2);line-height:1.55;">{rec['body']}</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            sh("📥", "Download Report", "#00ffa3")
            card('<b>ATS Analysis Report</b><br>'
                '<span style="font-size:.74rem;color:var(--t2);">Full breakdown: ATS score, semantic score, skill gaps, and AI recommendations.</span>')
           
            with open("ATS_Report.pdf", "rb") as pdf_file:
                st.download_button(
                    label="📥 Download ATS Report",
                    data=pdf_file,
                    file_name="ATS_Report.pdf",
                    mime="application/pdf"
                )

# ═══════════════════════════════════════════════════════════════════════════════
# RECRUITER SEARCH
# ═══════════════════════════════════s════════════════════════════════════════════
elif page == "Recruiter Search":

    sh("🔍", "Semantic Recruiter Search", "#00e5ff")
    card('<span style="font-size:.77rem;color:var(--t2);">Search the candidate pool using natural language. '
         'ChromaDB retrieves the best-matching profiles via MiniLM embeddings — no exact keyword match needed.</span>')

    st.markdown("<br>", unsafe_allow_html=True)
    qc, bc = st.columns([5,1])
    with qc:
        query = st.text_input("Search", placeholder='"Python ML engineer with NLP and AWS experience"', label_visibility="collapsed")
    with bc:
        search_btn = st.button("🔍 Search", use_container_width=True)

    f1, f2, f3 = st.columns(3)
    with f1: st.selectbox("Role", ["All Roles","Data Scientist","ML Engineer","DevOps","Backend"])
    with f2: st.selectbox("Experience", ["All Levels","Junior (0-2y)","Mid (2-5y)","Senior (5y+)"])
    with f3: min_sim = st.slider("Min Similarity", 0, 100, 50, format="%d%%")

    if search_btn and query.strip():
        with st.spinner("Querying vector index…"):
            time.sleep(0.5)
            
            results = search_resumes(
        query,
        top_n
    )

            documents = results["documents"][0]
            distances = results["distances"][0]

            real_results = []
            for i in range(len(documents)):
                score = round((1 / (1 + distances[i])) * 100, 2)
                real_results.append({
                    "name": f"Candidate {i+1}",
                    "role": "AI Candidate",
                    "exp": "N/A",
                    "score": score,
                    "snippet": documents[i][:250]
                })

            st.session_state.search_results = real_results
            

        sh("📋", f"{len(st.session_state.search_results)} results — \"{query[:40]}\"", "#00e5ff")
        for r in st.session_state.search_results:
            if r["score"] < min_sim: continue
            c = score_color(r["score"])
            st.markdown(f"""
            <div class="card">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:.4rem;">
                <div>
                  <span style="font-size:.88rem;font-weight:600;">{r['name']}</span>
                  <span style="font-size:.71rem;color:var(--t3);margin-left:.5rem;">{r['role']} · {r['exp']}</span>
                </div>
                <span style="font-family:'Syne',sans-serif;font-size:.9rem;font-weight:800;color:{c};">{r['score']}%</span>
              </div>
              <div style="height:3px;background:rgba(255,255,255,.05);border-radius:99px;margin-bottom:.4rem;">
                <div style="height:100%;width:{r['score']}%;background:{c};border-radius:99px;"></div>
              </div>
              <div style="font-size:.76rem;color:var(--t2);">{r['snippet']}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.info("Enter a query and click **Search** to find semantically matched candidates.", icon="🔍")


# ═══════════════════════════════════════════════════════════════════════════════
# RANKINGS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Rankings":

    sh("🏆", "Candidate Rankings", "#ffb300")

    results = search_resumes(
    "top candidates",
    top_n
)

    documents = results["documents"][0]

    distances = results["distances"][0]

    candidates = []

    for i in range(len(documents)):

        sem_score = round(
            (1 / (1 + distances[i])) * 100,
            1
        )

        ats_score = round(
            sem_score * 0.9,
            1
        )

        combined_score = round(
            (ats_score + sem_score) / 2,
            1
        )

        candidates.append({

            "name": f"Candidate {i+1}",

            "role": "AI Candidate",

            "ats": ats_score,

            "sem": sem_score,

            "combined": combined_score
        })
    filtered   = [c for c in candidates if c["combined"] >= min_score][:top_n]

    # Top candidate highlight
    if filtered:
        top = filtered[0]; c = score_color(top["combined"])
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(0,255,163,.08),rgba(0,229,255,.05));
                    border:1px solid rgba(0,255,163,.2);border-radius:18px;padding:1.75rem;
                    position:relative;margin-bottom:1.5rem;">
          <span style="position:absolute;top:1rem;right:1rem;font-size:.62rem;font-weight:700;
                       color:#00ffa3;background:rgba(0,255,163,.1);border:1px solid rgba(0,255,163,.25);
                       padding:.2rem .65rem;border-radius:99px;">★ TOP MATCH</span>
          <div style="font-family:'Syne',sans-serif;font-size:2.8rem;font-weight:800;color:{c};line-height:1;">
            {top['combined']}%</div>
          <div style="font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:700;">{top['name']}</div>
          <div style="font-size:.78rem;color:var(--t3);margin-bottom:.75rem;">{top['role']}</div>
          <span class="tag tag-green">ATS {top['ats']}%</span>
          <span class="tag tag-cyan">Semantic {top['sem']}%</span>
        </div>""", unsafe_allow_html=True)

    sh("📋", f"{len(filtered)} Candidates (min {min_score}%)", "#7c3aed")
    avatar_bgs = ["#7c3aed","#0096c7","#00b094","#e5383b","#f48c06"]

    for i, c in enumerate(filtered):
        color    = score_color(c["combined"])
        bg       = avatar_bgs[i % len(avatar_bgs)]
        initials = "".join(p[0] for p in c["name"].split()[:2])
        st.markdown(f"""
        <div class="card" style="display:flex;align-items:center;gap:1rem;padding:1rem 1.2rem;">
          <span style="font-family:'Syne',sans-serif;font-size:.72rem;font-weight:800;color:var(--t3);width:22px;">#{i+1}</span>
          <div style="width:34px;height:34px;border-radius:50%;background:{bg}22;color:{bg};border:1px solid {bg}44;
                      display:flex;align-items:center;justify-content:center;font-family:'Syne',sans-serif;
                      font-size:.75rem;font-weight:700;flex-shrink:0;">{initials}</div>
          <div style="flex:1;">
            <div style="font-size:.85rem;font-weight:600;">{c['name']}</div>
            <div style="font-size:.7rem;color:var(--t3);">{c['role']}</div>
          </div>
          <div style="width:140px;">
            <div style="display:flex;justify-content:space-between;font-size:.6rem;color:var(--t3);margin-bottom:3px;">
              <span>ATS {c['ats']}%</span><span>SEM {c['sem']}%</span></div>
            <div style="height:4px;background:rgba(255,255,255,.06);border-radius:99px;overflow:hidden;">
              <div style="height:100%;width:{c['combined']}%;background:{color};border-radius:99px;"></div>
            </div>
          </div>
          <span style="font-family:'Syne',sans-serif;font-size:.85rem;font-weight:800;
                       color:{color};min-width:40px;text-align:right;">{c['combined']}%</span>
        </div>""", unsafe_allow_html=True)

    with st.expander("⬇️ Export CSV"):
        df = pd.DataFrame(filtered)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download CSV", df.to_csv(index=False).encode(), "rankings.csv", "text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYTICS
# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Analytics":

    sh("📈", "Analytics Dashboard", "#7c3aed")

    results = search_resumes(
        "all candidates",
        top_n
    )

    documents = results["documents"][0]

    distances = results["distances"][0]

    data = []

    for i in range(len(documents)):

        sem_score = round(
            (1 / (1 + distances[i])) * 100,
            1
        )

        ats_score = round(
            sem_score * 0.9,
            1
        )

        combined_score = round(
            (ats_score + sem_score) / 2,
            1
        )

        data.append({

            "name":
            f"Candidate {i+1}",

            "role":
            "AI Candidate",

            "ats":
            ats_score,

            "sem":
            sem_score,

            "combined":
            combined_score
        })
    names  = [c["name"].split()[0] for c in data]
    ats_v  = [c["ats"]      for c in data]
    sem_v  = [c["sem"]      for c in data]
    comb_v = [c["combined"] for c in data]

    k1, k2, k3, k4 = st.columns(4)
    for col, label, val in zip([k1,k2,k3,k4],
        ["Candidates","Avg ATS","Avg Semantic","Avg Combined"],
        [len(data), f"{np.mean(ats_v):.1f}%", f"{np.mean(sem_v):.1f}%", f"{np.mean(comb_v):.1f}%"]):
        col.metric(label, val)

    st.markdown("<br>", unsafe_allow_html=True)
    CYAN, VIOLET, GREEN = "#00e5ff", "#7c3aed", "#00ffa3"
    tab1, tab2, tab3 = st.tabs(["Score Distribution", "ATS vs Semantic", "Candidate Comparison"])

    with tab1:
        fig, axes = plt.subplots(1, 3, figsize=(13, 4))
        for ax, vals, label, color in [(axes[0],ats_v,"ATS",CYAN),(axes[1],sem_v,"Semantic",VIOLET),(axes[2],comb_v,"Combined",GREEN)]:
            ax.hist(vals, bins=8, color=color+"55", edgecolor=color+"88")
            ax.axvline(np.mean(vals), color=color, lw=1.5, ls="--", label=f"μ={np.mean(vals):.0f}")
            ax.set_title(f"{label} Distribution", fontsize=9, fontweight="bold")
            ax.legend(fontsize=8, framealpha=0); ax.grid(axis="y", alpha=.4); ax.tick_params(labelsize=7)
        fig.tight_layout(); st.pyplot(fig, use_container_width=True); plt.close()

    with tab2:
        fig, ax = plt.subplots(figsize=(9, 4.5))
        ax.scatter(ats_v, sem_v, c=[score_color(s) for s in comb_v], s=110, edgecolors="#ffffff33", linewidths=.4, zorder=3)
        for c in data:
            ax.annotate(c["name"].split()[0], (c["ats"],c["sem"]), xytext=(6,3), textcoords="offset points", fontsize=7.5, alpha=.8)
        ax.axhline(70, color="#1a2240", lw=1, ls="--"); ax.axvline(70, color="#1a2240", lw=1, ls="--")
        ax.set_xlabel("ATS (%)"); ax.set_ylabel("Semantic (%)")
        ax.set_title("ATS vs Semantic Scatter", fontsize=11, fontweight="bold")
        ax.grid(alpha=.3); fig.tight_layout(); st.pyplot(fig, use_container_width=True); plt.close()

    with tab3:
        fig, ax = plt.subplots(figsize=(12, 4.5))
        x, w = np.arange(len(names)), 0.26
        ax.bar(x-w, ats_v,  w, label="ATS",      color=CYAN  +"66", edgecolor=CYAN,   lw=.5)
        ax.bar(x,   sem_v,  w, label="Semantic",  color=VIOLET+"66", edgecolor=VIOLET, lw=.5)
        ax.bar(x+w, comb_v, w, label="Combined",  color=GREEN +"66", edgecolor=GREEN,  lw=.5)
        ax.set_xticks(x); ax.set_xticklabels(names, rotation=30, ha="right", fontsize=8)
        ax.set_ylim(0, 110); ax.legend(fontsize=8, framealpha=0); ax.grid(axis="y", alpha=.3)
        ax.set_title("Score Comparison — All Candidates", fontsize=11, fontweight="bold")
        fig.tight_layout(); st.pyplot(fig, use_container_width=True); plt.close()

    st.markdown("<br>", unsafe_allow_html=True)
    sh("🎯", "Score Band Breakdown", "#00ffa3")
    bands = [
        ("Excellent (80+)", len([c for c in data if c["combined"]>=80]),  GREEN),
        ("Good (60–79)",    len([c for c in data if 60<=c["combined"]<80]), CYAN),
        ("Fair (40–59)",    len([c for c in data if 40<=c["combined"]<60]), "#ffb300"),
        ("Poor (<40)",      len([c for c in data if c["combined"]<40]),   "#ff4d7d"),
    ]
    for col, (label, count, color) in zip(st.columns(4), bands):
        pct = round(count/len(data)*100) if data else 0
        with col:
            card(f"""<div style="text-align:center;">
              <div style="font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;
                          color:{color};text-shadow:0 0 14px {color}44;">{count}</div>
              <div style="font-size:.67rem;color:{color};letter-spacing:.06em;text-transform:uppercase;margin:.15rem 0;">{pct}%</div>
              <div style="font-size:.73rem;color:var(--t3);">{label}</div>
            </div>""")