import streamlit as st
import pandas as pd
from database import get_stats, get_recent
from datetime import datetime

def render():
    stats = get_stats()
    st.markdown('<div class="hero"><div class="eyebrow">✦ YOUR AI COMMUNICATION COPILOT</div><h1>Write smarter. Communicate better.</h1><p>One intelligent workspace for confident email writing, clearer communication and proactive message security.</p></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-head"><div><div class="eyebrow">YOUR WORKSPACE</div><h2>At a glance</h2></div><div class="muted">Live insights · SQLite activity</div></div>', unsafe_allow_html=True)
    cols = st.columns(4)
    metrics = [("Emails generated",stats["generated"],"✉"),("Emails analysed",stats["analysed"],"◉"),("Phishing checks",stats["phishing"],"⬡"),("AI tasks completed",stats["tasks"],"✧")]
    for c,(label,value,ico) in zip(cols,metrics):
        with c: st.markdown(f'<div class="glass-card"><div class="metric-label">{ico} &nbsp;{label}</div><div class="metric-value">{value:,}</div><div class="metric-foot">Recorded in your local workspace</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section-head"><div><div class="eyebrow">PRODUCTIVITY</div><h2>Activity insights</h2></div></div>',unsafe_allow_html=True)
    left,right = st.columns([1.2,1])
    with left:
        counts=stats["by_feature"]
        if counts:
            df=pd.DataFrame({"Feature":list(counts.keys()),"Tasks":list(counts.values())}).sort_values("Tasks",ascending=False)
            st.bar_chart(df.set_index("Feature"), color="#9b83ff", height=260)
        else: st.info("Your activity chart will appear after your first AI task.")
    with right:
        recent=get_recent(6)
        if recent:
            for r in recent:
                st.markdown(f'<div class="activity-row"><b>{r["title"] or r["feature"]}</b><div class="muted">{r["feature"]} · {r["created_at"]}</div></div>',unsafe_allow_html=True)
        else: st.markdown('<div class="glass-card"><b>Your workspace is ready</b><p class="muted">Generated emails, analyses and AI tasks will appear here.</p></div>',unsafe_allow_html=True)
    st.markdown('<div class="section-head"><div><div class="eyebrow">QUICK ACCESS</div><h2>What would you like to do?</h2></div></div>',unsafe_allow_html=True)
    cards=[("✉","Create an email","Draft a polished message from a simple brief."),("⬡","Check a suspicious message","Inspect scam signals before you click."),("✎","Improve a draft","Make your writing clearer and more professional."),("◉","Understand the tone","Explore sentiment and emotional cues.")]
    cols=st.columns(4)
    for c,(ico,title,desc) in zip(cols,cards):
        with c: st.markdown(f'<div class="glass-card feature-card"><div class="feature-icon">{ico}</div><div class="feature-title">{title}</div><div class="feature-desc">{desc}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section-head"><div><div class="eyebrow">DAILY COACH</div><h2>Writing tip of the day</h2></div></div>',unsafe_allow_html=True)
    tips=["Put the purpose of your email in the first two sentences.","Use a specific subject line that tells the reader what action is needed.","Keep one main request per paragraph to make your message easy to scan.","Before sending, check names, dates, attachments and requested deadlines."]
    day=datetime.now().timetuple().tm_yday
    st.markdown(f'<div class="glass-card">💡 &nbsp;{tips[day % len(tips)]}</div>',unsafe_allow_html=True)
