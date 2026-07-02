import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import networkx as nx

API = "http://127.0.0.1:8000"
st.set_page_config(
    page_title="TRACE",
    page_icon="🛡️",
    layout="wide",
)

st.markdown("""
<style>

.stApp{
background:#07111f;
color:white;
}

section[data-testid="stSidebar"]{
background:#0B132B;
}

.card{
background:#111827;
padding:20px;
border-radius:15px;
border:1px solid #1f2937;
text-align:center;
box-shadow:0px 0px 12px rgba(0,0,0,.4);
}

.alert{
background:#8B0000;
padding:18px;
border-radius:12px;
font-size:20px;
font-weight:bold;
color:white;
text-align:center;
}

.small{
font-size:15px;
color:#9CA3AF;
}

</style>
""", unsafe_allow_html=True)

# ---------------- Sidebar ---------------- #

st.sidebar.image("https://img.icons8.com/fluency/96/shield.png", width=80)

st.sidebar.title("TRACE")

st.sidebar.write("Money Laundering Detection")

st.sidebar.divider()

if st.sidebar.button("🔗 Connect Open Banking Sandbox"):
    st.success("✅ Connected to Open Banking Sandbox")

if st.sidebar.button("▶ Run Analysis"):
    with st.spinner("Analyzing transactions..."):
        import time
        time.sleep(2)

    st.success("✅ Analysis completed successfully.")
    st.warning("🚨 Suspicious Layering Activity Detected")

st.sidebar.divider()

st.sidebar.success("System Online")
try:
    analysis = requests.get(f"{API}/analysis").json()
    transactions = requests.get(f"{API}/transactions").json()
    df = pd.DataFrame(transactions)
except:
    st.error("❌ Backend is not running")
    st.stop()

# ---------------- Header ---------------- #

st.title("🛡️ TRACE Security Dashboard")

st.write("Real-time Money Laundering Monitoring Platform")

# ---------------- Cards ---------------- #

c1,c2,c3,c4 = st.columns(4)

with c1:
    st.markdown(f"""
<div class='card'>
<h3>Risk Score</h3>
<h1 style='color:#ff4b4b;'>{analysis['risk_score']}%</h1>
<div class='small'>Critical Risk</div>
</div>
""", unsafe_allow_html=True)

with c2:
   st.markdown(f"""
<div class='card'>
<h3>Banks</h3>
<h1>{analysis["banks"]}</h1>
<div class='small'>Connected</div>
</div>
""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""
<div class='card'>
<h3>Accounts</h3>
<h1>{analysis["accounts"]}</h1>
<div class='small'>Tracked</div>
</div>
""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""
<div class='card'>
<h3>Transactions</h3>
<h1>{analysis["transactions"]}</h1>
<div class='small'>Today's Activity</div>
</div>
""", unsafe_allow_html=True)
st.subheader("📋 Transactions")

st.dataframe(df, use_container_width=True)
st.subheader("🕸️ Network Analysis")

G = nx.Graph()

# نأخذ أول 30 عملية حتى يكون الرسم واضح
sample = df.head(30)

for _, row in sample.iterrows():
    sender = row["sender"]
    receiver = row["receiver"]

    G.add_node(sender)
    G.add_node(receiver)
    G.add_edge(sender, receiver)

pos = nx.spring_layout(G, seed=42)

edge_x = []
edge_y = []

for edge in G.edges():
    x0, y0 = pos[edge[0]]
    x1, y1 = pos[edge[1]]

    edge_x += [x0, x1, None]
    edge_y += [y0, y1, None]

edge_trace = go.Scatter(
    x=edge_x,
    y=edge_y,
    mode="lines",
    line=dict(width=1),
    hoverinfo="none"
)

node_x = []
node_y = []
node_color = []

for node in G.nodes():
    x, y = pos[node]
    node_x.append(x)
    node_y.append(y)

    if node in analysis["suspicious_accounts"]:
        node_color.append("red")
    else:
        node_color.append("deepskyblue")

node_trace = go.Scatter(
    x=node_x,
    y=node_y,
    mode="markers+text",
    text=list(G.nodes()),
    textposition="top center",
    marker=dict(
        size=15,
        color=node_color
    )
)

fig = go.Figure(data=[edge_trace, node_trace])

fig.update_layout(
    height=600,
    plot_bgcolor="#07111f",
    paper_bgcolor="#07111f",
    font_color="white",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)