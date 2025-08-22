import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import MaxNLocator
import pandas as pd

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

# -------------------- STYLE --------------------
st.markdown("""
<style>
/* App background */
.stApp { background: linear-gradient(135deg, #0f172a, #1e293b); color: #e5e7eb; }

/* Headings */
.neon-title {
  text-align:center; font-size:48px; font-weight:800; letter-spacing:0.5px;
  color:#60a5fa; text-shadow:0 0 22px rgba(96,165,250,0.65);
  animation: fadeInDown 0.8s ease;
}
.subtle-sub {
  text-align:center; font-size:18px; color:#cbd5e1; margin-top:6px;
  animation: fadeIn 1s ease 0.2s both;
}

/* Big info box (high contrast) */
.info-box {
  background: linear-gradient(145deg, rgba(31,41,55,0.95), rgba(17,24,39,0.95));
  border: 1px solid rgba(148,163,184,0.2);
  border-radius: 18px;
  padding: 34px;
  margin: 22px auto;
  width: min(900px, 92%);
  color: #f8fafc;
  font-size: 18px;
  line-height: 1.9;
  box-shadow: 0 20px 40px rgba(0,0,0,0.35);
  backdrop-filter: blur(10px);
  animation: fadeIn 0.8s ease 0.15s both;
}
.info-box b { color:#93c5fd; }

/* CTA pill */
.cta {
  width: min(900px, 92%);
  margin: 12px auto 0;
  text-align:center;
  background: #1E3A8A;
  border: 1px solid rgba(255,255,255,0.05);
  color: #fff; padding: 14px 16px; border-radius: 12px;
  font-size: 18px; box-shadow: 0 10px 24px rgba(30,58,138,0.45);
  animation: fadeInUp 0.8s ease 0.2s both;
}

/* Section headers */
.section-title {
  font-size: 26px; font-weight: 700; color: #93c5fd;
  margin: 18px 0 6px; text-shadow: 0 0 12px rgba(147,197,253,0.25);
}

/* Sidebar */
[data-testid="stSidebar"] {
  background: #111827;
  border-right: 1px solid rgba(148,163,184,0.2);
}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] label, .st-emotion-cache-1y4p8pa {
  color: #e5e7eb !important;
}

/* Animations */
@keyframes fadeIn { from {opacity:0} to {opacity:1} }
@keyframes fadeInDown { from {opacity:0; transform: translateY(-14px)} to {opacity:1; transform: translateY(0)} }
@keyframes fadeInUp { from {opacity:0; transform: translateY(14px)} to {opacity:1; transform: translateY(0)} }
</style>
""", unsafe_allow_html=True)

# -------------------- SIDEBAR --------------------
with st.sidebar:
    st.markdown("## 📂 Upload Your Chat")
    st.caption("Export from WhatsApp → *Without Media* → upload the `.txt` file.")
    uploaded_file = st.file_uploader("Drag & drop or browse", type=["txt"])
    st.markdown("---")

# Keep button state so page never blanks on rerun
if "show_analysis" not in st.session_state:
    st.session_state["show_analysis"] = False

# -------------------- WELCOME (NO FILE) --------------------
if uploaded_file is None and not st.session_state["show_analysis"]:
    st.markdown('<div class="neon-title">💬 WhatsApp Chat Analyzer</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle-sub">Turn your chats into crisp, visual insights — fast.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box">
      <div style="font-size:22px; font-weight:700; margin-bottom:8px; color:#93c5fd;">ℹ️ How to use</div>
      ✅ <b>Step 1:</b> Open WhatsApp → Select a chat → <b>Export chat → Without media</b><br/>
      ✅ <b>Step 2:</b> Upload the exported <b>.txt</b> using the left sidebar<br/>
      ✅ <b>Step 3:</b> Pick <b>Overall</b> or a specific participant<br/>
      ✅ <b>Step 4:</b> Click <b>Show Analysis</b> to generate insights 🚀<br/><br/>

      <b>What you’ll see</b><br/>
      • 📈 Top stats (messages, words, media, links)<br/>
      • 🗓️ Monthly & daily timelines<br/>
      • 🗺️ Most active days & months + weekly heatmap<br/>
      • 🏆 Most active users (for Overall view)<br/>
      • ☁️ Word cloud & most common words<br/>
      • 😂 Emoji analysis with share breakdown<br/>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="cta">👉 Upload your chat from the left sidebar to begin</div>', unsafe_allow_html=True)
    st.stop()

# -------------------- FILE LOADED --------------------
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    # Build user list
    user_list = df['user'].dropna().unique().tolist()
    user_list = [u for u in user_list if u != "group_notification"]
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("👤 Select user", user_list, index=0)

    # Primary action (persistent)
    if st.sidebar.button("🚀 Show Analysis", type="primary"):
        st.session_state["show_analysis"] = True

    # Helpful status
    if not st.session_state["show_analysis"]:
        st.success("✅ File uploaded! Select a user and click **Show Analysis** to proceed.")
        st.stop()

# -------------------- ANALYSIS --------------------
# From here on, we know we have a file and button was pressed
with st.spinner("Crunching your chat… this won’t take long ⏳"):
    # Safety: if selected user has no messages, handle gracefully
    df_scope = df if selected_user == "Overall" else df[df['user'] == selected_user]
    if df_scope.empty:
        st.warning("No messages found for this selection. Try another user or Overall.")
        st.stop()

    # -------- Top Statistics --------
    st.markdown('<div class="section-title">📊 Top Statistics</div>', unsafe_allow_html=True)
    num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Messages", int(num_messages))
    c2.metric("Total Words", int(words))
    c3.metric("Media Shared", int(num_media_messages))
    c4.metric("Links Shared", int(num_links))

    # -------- Monthly Timeline --------
    st.markdown('<div class="section-title">🗓️ Monthly Timeline</div>', unsafe_allow_html=True)
    timeline = helper.monthly_timeline(selected_user, df)
    if not timeline.empty:
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], linewidth=2)
        ax.set_xlabel("Month")
        ax.set_ylabel("Messages")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("No monthly data available for the current selection.")

    # -------- Daily Timeline --------
    st.markdown('<div class="section-title">📅 Daily Timeline</div>', unsafe_allow_html=True)
    daily_timeline = helper.daily_timeline(selected_user, df)
    if not daily_timeline.empty:
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], linewidth=2)
        ax.set_xlabel("Date")
        ax.set_ylabel("Messages")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    else:
        st.info("No daily data available for the current selection.")

    # -------- Activity Map (Busy Day / Busy Month) --------
    st.markdown('<div class="section-title">📌 Activity Map</div>', unsafe_allow_html=True)
    a1, a2 = st.columns(2)
    with a1:
        st.subheader("Most Busy Day")
        busy_day = helper.week_activity_map(selected_user, df)
        if not busy_day.empty:
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            ax.yaxis.set_major_locator(MaxNLocator(integer=True))
            plt.xticks(rotation=0)
            st.pyplot(fig)
        else:
            st.info("No weekday activity available.")

    with a2:
        st.subheader("Most Busy Month")
        busy_month = helper.month_activity_map(selected_user, df)
        if not busy_month.empty:
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values)
            plt.xticks(rotation=0)
            st.pyplot(fig)
        else:
            st.info("No month-wise activity available.")

    # -------- Weekly Activity Heatmap --------
    st.markdown('<div class="section-title">🔥 Weekly Activity Heatmap</div>', unsafe_allow_html=True)
    user_heatmap = helper.activity_heatmap(selected_user, df)
    if isinstance(user_heatmap, pd.DataFrame) and not user_heatmap.empty:
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, cmap="YlGnBu", ax=ax)
        ax.set_xlabel("Hour")
        ax.set_ylabel("Day")
        st.pyplot(fig)
    else:
        st.info("Not enough data to render heatmap.")

    # -------- Most Active Users (Overall only) --------
    if selected_user == "Overall":
        st.markdown('<div class="section-title">🏆 Most Active Users</div>', unsafe_allow_html=True)
        try:
            x, new_df = helper.most_busy_users(df)
            m1, m2 = st.columns(2)
            with m1:
                if not x.empty:
                    fig, ax = plt.subplots()
                    ax.bar(x.index, x.values)
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(fig)
                else:
                    st.info("No active users to display.")
            with m2:
                st.dataframe(new_df)
        except Exception:
            st.info("Could not compute most active users for this dataset.")

    # -------- Word Cloud --------
    st.markdown('<div class="section-title">☁️ Word Cloud</div>', unsafe_allow_html=True)
    try:
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)
    except Exception:
        st.info("Word cloud is unavailable for this selection.")

    # -------- Most Common Words --------
    st.markdown('<div class="section-title">💬 Most Common Words</div>', unsafe_allow_html=True)
    try:
        most_common_df = helper.most_common_words(selected_user, df)
        if not most_common_df.empty:
            fig, ax = plt.subplots()
            ax.barh(most_common_df[0], most_common_df[1])
            ax.invert_yaxis()
            st.pyplot(fig)
        else:
            st.info("No common words to display.")
    except Exception:
        st.info("Could not compute common words for this selection.")

    # -------- Emoji Analysis --------
    st.markdown('<div class="section-title">😂 Emoji Analysis</div>', unsafe_allow_html=True)
    try:
        emoji_df = helper.emoji_helper(selected_user, df)
        e1, e2 = st.columns(2)
        with e1:
            st.dataframe(emoji_df)
        with e2:
            if not emoji_df.empty:
                top = emoji_df.head(5)
                fig, ax = plt.subplots()
                ax.pie(top[1], labels=top[0], autopct="%0.2f")
                st.pyplot(fig)
            else:
                st.info("No emojis found.")
    except Exception:
        st.info("Could not compute emoji analysis for this selection.")
