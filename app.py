# Imports
import streamlit as st
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.express as px
import requests 

st.set_page_config(
    
    layout="wide",
   
)

st.markdown(
    """
    <style>
        /* Spricht den Hauptcontainer von Streamlit an */
        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 0rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style='border-bottom: 1px solid #374151; padding-bottom: 8px; margin-bottom: 24px;'>
        <h1 style='font-family: "Inter", sans-serif; font-size: 22px; font-weight: 500; color: #F9FAFB; margin: 0; letter-spacing: 1px; text-transform: uppercase;'>
            Portfolio Analytics
            <span style='color: #6B7280; font-weight: 400; font-size: 14px; margin-left: 12px; letter-spacing: normal; text-transform: none;'>
                | v1.0
            </span>
        </h1>
    </div>
    """,
    unsafe_allow_html=True
)


name_mapping = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "NVIDIA",
    "SAP": "SAP",
    "ALV.DE": "Allianz",
    "RHM.DE": "Rheinmetall"
}

# Data
stocks = [
    "AAPL",
    "MSFT",
    "NVDA",
    "SAP",
    "ALV.DE",
    "RHM.DE"
]

@st.cache_data(ttl=3600)
def search_global_tickers(query):
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        results = {}
        for quote in data.get('quotes', []):
            if quote.get('quoteType') in ['EQUITY', 'ETF']:
                symbol = quote['symbol']
                name = quote.get('shortname', 'Unbekannt')
                exchange = quote.get('exchDisp', '')
                results[symbol] = f"{name} ({exchange})"
        return results
    except Exception as e:
        return {}
    
if "my_portfolio" not in st.session_state:
   
    st.session_state.my_portfolio = []
if "my_mapping" not in st.session_state:
    st.session_state.my_mapping = name_mapping.copy()

# =========================================
# Portfolio Settings
# =========================================

with st.expander("Portfolio Settings", expanded=True):
    
    
    search_term = st.text_input(
        "Search for new assets",
        placeholder="e.g. Amazon, MSCI World,..."
    )
    
    if search_term:
        search_results = search_global_tickers(search_term)
        
        if search_results:
            
            new_selection = st.multiselect(
                "Found matches:",
                options=list(search_results.keys()),
                format_func=lambda x: f"{x} | {search_results[x]}",
                help="Choose assets to add to your portfolio."
            )
            
            
            if new_selection:
                for ticker in new_selection:
                    if ticker not in st.session_state.my_portfolio:
                        st.session_state.my_portfolio.append(ticker)
                        st.session_state.my_mapping[ticker] = search_results[ticker]
                st.success("Asset(s) succesfully found.")
        else:
            st.warning("No matches found.")

    selected_stocks = st.multiselect(
        "Selected assets",
        options=st.session_state.my_portfolio,
        default=st.session_state.my_portfolio, 
        format_func=lambda x: st.session_state.my_mapping.get(x, x),
    )

    # =========================================
    # Time Period
    # =========================================

    col1, col2 = st.columns(2)

    start_date = col1.date_input(
        "Start",
        value=pd.to_datetime("2020-01-01")
    )

    end_date = col2.date_input(
        "End",
        value=pd.to_datetime("today")
    )

    # =========================================
    # Benchmark
    # =========================================

    benchmark_names = {
    "MSCI World ETF": "URTH",
    "S&P 500 ETF": "SPY",
    "Nasdaq 100 ETF": "QQQ"
}

    benchmark_label = st.selectbox(
    "Benchmark",
    options=list(benchmark_names.keys())
)

    benchmark = benchmark_names[benchmark_label]

    simulations = st.slider(
        "Monte Carlo Simulations",
        min_value=1000,
        max_value=100000,
        value=10000,
        step=1000,
        help="Higher values improve precision but increase runtime."
    )

    random_seed = st.number_input(
        "Random Seed",
        value=42,
        step=1
    )
 # Validation
    if len(selected_stocks) < 2:

        st.warning(
            "Please select at least two stocks."
        )

        st.stop()

@st.cache_data
def load_data(
    stocks,
    start_date,
    end_date
):

    data = yf.download(
        stocks,
        start=start_date,
        end=end_date
    )["Close"]

    return data

data = load_data(
    selected_stocks,
    start_date,
    end_date
)
data = data.rename(columns=name_mapping)

benchmark_prices = yf.download(
    benchmark,
    start=start_date,
    end=end_date
)["Close"].squeeze()


# Efficient Frontier

returns = data.pct_change(fill_method=None).fillna(0)

np.random.seed=(random_seed)

annual_return = returns.mean() * 252
cov_matrix = returns.cov() * 252

portfolio_returns = []
portfolio_volatility = []
portfolio_sharpe = []
portfolio_weights = []

num_assets = len(returns.columns)

for i in range(simulations):

    weights = np.random.random(num_assets)
    weights /= np.sum(weights)

    ret = weights @ annual_return

    vol = np.sqrt(
        weights.T @ cov_matrix @ weights
    )

    sharpe = ret / vol

    portfolio_returns.append(ret * 100)
    portfolio_volatility.append(vol * 100)
    portfolio_sharpe.append(sharpe)
    portfolio_weights.append(weights)

frontier = pd.DataFrame({
    "Return": portfolio_returns,
    "Volatility": portfolio_volatility,
    "Sharpe": portfolio_sharpe
})

max_sharpe = frontier["Sharpe"].idxmax()

best_return = frontier.loc[max_sharpe, "Return"]
best_vol = frontier.loc[max_sharpe, "Volatility"]
best_weights = portfolio_weights[max_sharpe]

frontier_fig = px.scatter(

    frontier,

    x="Volatility",
    y="Return",

    color="Sharpe",

    color_continuous_scale="Blues"
)

frontier_fig.update_layout(
    
    template="plotly_dark",

    paper_bgcolor="#0E1117", 
    plot_bgcolor="#0E1117",

    width=1800,
    height=550,

    font=dict(
        color="#F9FAFB",
        size=18
    ),
     hoverlabel=dict(
        bgcolor="#111827",
        font_size=14
    ),

    margin=dict(t=0),

    showlegend=False
)

frontier_fig.update_traces(
    opacity=0.7, 

    hovertemplate= "<b>Portfolio Simulation</b><br><br>" +

    "Return: %{y:.2f}%<br>" +

    "Volatility: %{x:.2f}%<br>" +

    "Sharpe Ratio: %{marker.color:.2f}" +

    "<extra></extra>")

frontier_fig.add_scatter(

    x=[best_vol],
    y=[best_return],

    mode="markers+text",

    text=["Max Sharpe"],

    textposition="top left",

    marker=dict(
        size=24,
        color="gold",
        symbol="star",
        line=dict(
            width=2,
            color="white"
        )
    )  
)

frontier_fig.update_layout(margin=dict(t=0))

best_sharpe=best_return/best_vol

frontier_fig.data[-1].hovertemplate = (
    "<b>Maximum Sharpe Portfolio</b><br><br>"
    f"Return: {best_return:.2f}%<br>"
    f"Volatility: {best_vol:.2f}%<br>"
    f"Sharpe Ratio: {best_sharpe:.2f}"
    "<extra></extra>"
)

#Allocation

allocation = pd.DataFrame({
    "Company": data.columns,
    "Weight": best_weights * 100
})

allocation["Company"] = allocation["Company"].apply(
    lambda x: st.session_state.my_mapping.get(x, x)
)

allocation = allocation.sort_values(
    by="Weight",
    ascending=False
)
allocation["Weight"] = allocation["Weight"].round(2)

threshold = 2.0  

main_positions = allocation[allocation["Weight"] >= threshold]
small_positions = allocation[allocation["Weight"] < threshold]

if not small_positions.empty:
    others_sum = small_positions["Weight"].sum()
    others_row = pd.DataFrame([{"Company": "Others", "Weight": round(others_sum, 2)}])
    
    allocation = pd.concat([main_positions, others_row], ignore_index=True)

color_map = {
    "Apple": "#E0E0E0",
    "Microsoft": "#ED6028",
    "NVIDIA": "#78D636",
    "SAP": "#00BBFF",
    "Allianz": "#0D05FF",
    "Rheinmetall": "#8480FF",
    "Others": "#4B5563"
}

allocation_fig = px.pie(
    allocation,
    names="Company",   
    values="Weight",
    hole=0.3,
    color="Company",   
    color_discrete_map=color_map,
    color_discrete_sequence=px.colors.qualitative.Dark24,
)

allocation_fig.update_layout(

    template="plotly_dark",

    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",

    hoverlabel=dict(
        bgcolor="#111827",
        font_size=20
    ),
    height=550,
    margin=dict(t=0),
    showlegend=False,
    legend=dict(
        font=dict(size=20),
        x=0.85,
        y=0.9
    )

    )

allocation_fig.update_traces(

    marker=dict(
        line=dict(
            color="#1F2937",
            width=0.5
        )
    ),
    textinfo="none",
    textposition="auto",

    textfont_size=28,

    insidetextorientation="horizontal",

    hovertemplate=
    "<b>%{label}</b><br><br>" +

    "Weight: %{value:.1f}%<br>" +

    "<extra></extra>"
)

#Performance

portfolio_returns = returns.dot(best_weights)

benchmark_returns = (
    benchmark_prices.pct_change(fill_method=None)
    .dropna()
)

portfolio_cum = (
    1 + portfolio_returns
).cumprod()

benchmark_cum = (
    1 + benchmark_returns
).cumprod()

cum_df = pd.DataFrame({
    "Portfolio": portfolio_cum,
    "Benchmark": benchmark_cum
}).dropna()

cum_df = (
    (cum_df - 1) * 100
)

cumulative_fig = px.line(
     cum_df,
)

portfolio_end = cum_df["Portfolio"].iloc[-1]
benchmark_end = cum_df["Benchmark"].iloc[-1]

last_date = cum_df.index[-1].strftime("%Y-%m-%d")

cumulative_fig.add_annotation(x=last_date,

    y=portfolio_end,

    text=f"{portfolio_end:.0f}%",

    showarrow=False,

    xshift=35,
    yshift=10
)
cumulative_fig.add_annotation(

    x=last_date,

    y=benchmark_end,

    text=f"{benchmark_end:.0f}%",

    showarrow=False,

    xshift=35,
    yshift=10
)

cumulative_fig.data[0].line.width = 2.5
cumulative_fig.data[1].line.width = 2
cumulative_fig.data[1].opacity = 0.6

cumulative_fig.update_layout(

    template="plotly_dark",

    paper_bgcolor="#0E1117",

    plot_bgcolor="#0E1117",

    width=1800,
    height=600,

    legend_title_text="",

    margin=dict(t=0),

    font=dict(
        color="#F9FAFB",
        size=16
    ),

    hoverlabel=dict(
        bgcolor="#111827",
        font_size=14
    )
    
)
cumulative_fig.data[0].line.color = "#60A5FA"
cumulative_fig.data[1].line.color = "#EF4444"

cumulative_fig.update_xaxes(
    title=""
)

cumulative_fig.update_yaxes(
    title="Cumulative Returns (%)"
)

cumulative_fig.update_traces(

    hovertemplate=
    "<b>%{fullData.name}</b><br><br>" +

    "Date: %{x}<br>" +

    "Return: %{y:.2f}%" +

    "<extra></extra>"
)

# Drawdown 

def calculate_drawdown(series):

    clean_series = series.fillna(0) 

    cumulative = (1 + clean_series).cumprod()

    running_max = cumulative.cummax()

    drawdown = (
        (cumulative - running_max)
        / running_max
    ) * 100

    return drawdown

portfolio_drawdown = calculate_drawdown(
    portfolio_returns
)
benchmark_drawdown = calculate_drawdown(
    benchmark_returns
)

drawdown_df = pd.DataFrame({
    "Portfolio": portfolio_drawdown,
    "Benchmark": benchmark_drawdown
}).dropna()

portfolio_max_dd = portfolio_drawdown.min()
portfolio_max_date = portfolio_drawdown.idxmin()

benchmark_max_dd = benchmark_drawdown.min()
benchmark_max_date = benchmark_drawdown.idxmin()

drawdown_fig = px.line(

    drawdown_df,
)
drawdown_fig.add_scatter(

    x=[portfolio_max_date.strftime("%Y-%m-%d")],

    y=[portfolio_max_dd],

    mode="markers+text",

    text=[
        f"Portfolio Max DD: {portfolio_max_dd:.1f}%",
        
    ],

    textposition="middle right",

    marker=dict(
        size=7,
        color="#60A5FA",
        line=dict(
            width=1,
            color="white"
        )
    ),

    showlegend=False
)

drawdown_fig.add_scatter(
x=[benchmark_max_date.strftime("%Y-%m-%d")],

    y=[benchmark_max_dd],

    mode="markers+text",

    text=[
        f"Benchmark Max DD: {benchmark_max_dd:.1f}%"
    ],

    textposition="middle right",

    marker=dict(
        size=7,
        color="#EF4444",
        line=dict(
            width=1,
            color="white"
        )
    ),

    showlegend=False
)

drawdown_fig.data[0].line.color = "#60A5FA"
drawdown_fig.data[1].line.color = "#EF4444"

drawdown_fig.data[0].opacity = 0.5
drawdown_fig.data[1].opacity = 0.35

drawdown_fig.update_layout(

    template="plotly_dark",

    paper_bgcolor="#0E1117",

    plot_bgcolor="#0E1117",

    width=1800,
    height=600,

    hoverlabel=dict(
        bgcolor="#111827",
        font_size=14
    ),
    margin=dict(t=0),
    legend_title_text="",
    font=dict(
        color="#F9FAFB",
        size=16
    )
)

drawdown_fig.update_xaxes(title="")

drawdown_fig.update_yaxes(
    title="Drawdown (%)"
)

drawdown_fig.update_traces(
    fill="tozeroy",
    line=dict(width=1.5),)
# Portfolio Line
drawdown_fig.data[0].hovertemplate = (
    "<b>Portfolio</b><br><br>" +
    "Date: %{x}<br>" +
    "Drawdown: %{y:.2f}%<br>" +
    "<extra></extra>"
)

# Benchmark Line
drawdown_fig.data[1].hovertemplate = (
    "<b>Benchmark</b><br><br>" +
    "Date: %{x}<br>" +
    "Drawdown: %{y:.2f}%<br>" +
    "<extra></extra>"
)

# Portfolio Marker
drawdown_fig.data[2].hovertemplate = (
    "<b>Portfolio Max Drawdown</b><br><br>" +
    "Date: %{x}<br>" +
    "Drawdown: %{y:.2f}%<br>" +
    "<extra></extra>"
)

# MSCI Marker
drawdown_fig.data[3].hovertemplate = (
    "<b>Benchmark Max Drawdown</b><br><br>" +
    "Date: %{x}<br>" +
    "Drawdown: %{y:.2f}%<br>" +
    "<extra></extra>"
)

# Rolling Sharpe Function
def rolling_sharpe(series, window=252):
    rolling_return = series.rolling(window).mean() * 252
    rolling_volatility = series.rolling(window).std() * np.sqrt(252)
    return rolling_return / rolling_volatility

# DataFrame erstellen
rolling_df = pd.concat(
    [
        rolling_sharpe(portfolio_returns).rename("Portfolio"),
        rolling_sharpe(benchmark_returns).rename("Benchmark")
    ],
    axis=1
).dropna()

# Figur erstellen
rolling_fig = px.line(rolling_df)

# Layout anpassen
rolling_fig.update_layout(
    legend_title_text="",
    template="plotly_dark",
    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",
    width=1800,
    height=600,
    font=dict(color="#F9FAFB", size=20),
    margin=dict(t=0),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#111827",
        font_size=14
    )
)

# Y-Achse anpassen
rolling_fig.update_yaxes(title="Rolling Sharpe Ratio")

# Nulllinie hinzufügen
rolling_fig.add_hline(
    y=0,
    line_dash="dash",
    line_color="gray",
    opacity=0.6
)

rolling_fig.layout.shapes[0].update(layer="below")

# Linien-Dicken und Transparenz anpassen
rolling_fig.data[0].line.width = 2.5
rolling_fig.data[1].line.width = 2
rolling_fig.data[1].opacity = 0.6
rolling_fig.data[0].line.color = "#60A5FA"   # Blau
rolling_fig.data[1].line.color = "#EF4444"   # Rot

# Hover-Template korrigieren
rolling_fig.update_traces(
    hovertemplate="<b>%{data.name}</b><br>" +
                  "Date: %{x|%Y-%m-%d}<br>" +
                  "Rolling Sharpe Ratio: %{y:.2f}" +
                  "<extra></extra>"
)

#Correlations

corr = returns.corr()

mapped_names = [st.session_state.my_mapping.get(ticker, ticker) for ticker in corr.columns]
corr.columns = mapped_names
corr.index = mapped_names

correlation_fig = px.imshow(
    corr,

    text_auto=".2f",

    range_color=[-1, 1],

    color_continuous_scale="RdBu",

    labels=dict(
        x="Corporation",
        y="Corporation",
        color="Correlation"
    )
)
correlation_fig.update_layout(

    template="plotly_dark",

    paper_bgcolor="#0E1117",
    plot_bgcolor="#0E1117",

    width=1200,
    height=700,

    font=dict(
        color="#F9FAFB",
        size=43
    ),
    margin=dict(t=0),

    hoverlabel=dict(
        bgcolor="#111827",
        font_size=14
    ),

    coloraxis_colorbar=dict(
        thickness=25,
        len=0.7
         )
)
correlation_fig.update_traces(

    xgap=4,
    ygap=4,

    hovertemplate=
    "Asset 1: %{x}<br>" +
    "Asset 2: %{y}<br>" +
    "Correlation: %{z:.2f}<extra></extra>"
)

correlation_fig.update_xaxes(
    tickangle=-35,
    gridcolor="#374151",
    tickfont=dict(size=14)
)

correlation_fig.update_yaxes(
    tickangle=0,
    gridcolor="#374151",
    tickfont=dict(size=18)
)

# =========================================
# KPI Cards
# =========================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    with st.container(height=160, border=True): # Sharpe Ratio Color
    
        if best_sharpe >= 1.5:

         sharpe_color = "#22C55E"   # Green

        elif best_sharpe >= 1:

         sharpe_color = "#84CC16"   # Light Green

        elif best_sharpe >= 0.5:

         sharpe_color = "#F59E0B"   # Orange

        else:

         sharpe_color = "#EF4444"   # Red
        st.markdown(
            f"""
            <div style="padding-top:0.2rem;">

             <div style="
            font-size:1.2rem;
            font-weight:600;
            margin-bottom:0.8rem;
            ">
            Sharpe Ratio
             </div>

            <div style="
            color:{sharpe_color};
            font-size:3rem;
            font-weight:700;
            line-height:1;
            margin-bottom:0.8rem;
            ">
            {best_sharpe:.2f}
             </div>

             <div style="
            color:#9CA3AF;
            font-size:1rem;
             ">
            Risk-adjusted return
             </div>

            </div>
            """,
            unsafe_allow_html=True,

help="Ratio between return and volatility. Higher Sharpe Ratios indicate better risk-adjusted returns." 
        )

with col2:

    with st.container(height=160, border=True):
        if best_return >0:

         return_color = "#22C55E"   # Green
        else:

         return_color = "#EF4444"   # Red

        st.markdown(
            f"""
            <div style="padding-top:0.2rem;">

             <div style="
            font-size:1.2rem;
            font-weight:600;
            margin-bottom:0.8rem;
            ">
            Return
             </div>

            <div style="
            color:{return_color};
            font-size:3rem;
            font-weight:700;
            line-height:1;
            margin-bottom:0.8rem;
            ">
            {best_return:.1f} %
             </div>

             <div style="
            color:#9CA3AF;
            font-size:1rem;
             ">
            Annualized return
             </div>

            </div>
            """,
            unsafe_allow_html=True
        )
with col3:

    with st.container(height=160, border=True):
        
        if best_vol <15:

         vol_color = "#22C55E"   # Green

        elif best_vol<=25:

         vol_color = "#FBFF00"   # Yellow

        elif best_vol>25:

         vol_color = "#F59E0B"   # Orange

        st.markdown(
            f"""
            <div style="padding-top:0.2rem;">

             <div style="
            font-size:1.2rem;
            font-weight:600;
            margin-bottom:0.8rem;
            ">
            Volatility
             </div>

            <div style="
            color:{vol_color};
            font-size:3rem;
            font-weight:700;
            line-height:1;
            margin-bottom:0.8rem;
            ">
            {best_vol:.1f} %
             </div>

             <div style="
            color:#9CA3AF;
            font-size:1rem;
             ">
            Annualized volatility
             </div>

            </div>
            """,
            unsafe_allow_html=True
        )

with col4:

    with st.container(height=160, border=True):
        if portfolio_max_dd >=-25:

         dd_color = "#22C55E"   # Green

        elif portfolio_max_dd>=-35:

         dd_color = "#FBFF00"   # Yellow

        elif portfolio_max_dd>=-45:

         dd_color = "#F59E0B"   # Orange

        else:

         dd_color = "#EF4444"   # Red
        st.markdown(
            f"""
            <div style="padding-top:0.2rem;">

             <div style="
            font-size:1.2rem;
            font-weight:600;
            margin-bottom:0.8rem;
            ">
            Drawdown
             </div>

            <div style="
            color:{dd_color};
            font-size:3rem;
            font-weight:700;
            line-height:1;
            margin-bottom:0.8rem;
            ">
            {portfolio_max_dd:.1f} %
             </div>

             <div style="
            color:#9CA3AF;
            font-size:1rem;
             ">
            Largest portfolio decline
             </div>

            </div>
            """,
            unsafe_allow_html=True
        )

with col5:

    with st.container(height=160, border=True):

        st.markdown(
            f"""
            <div style="padding-top:0.2rem;">

             <div style="
            font-size:1.2rem;
            font-weight:600;
            margin-bottom:0.8rem;
            ">
            Stocks
             </div>

            <div style="
            color:FFFFFF;
            font-size:3rem;
            font-weight:700;
            line-height:1;
            margin-bottom:0.8rem;
            ">
            {len(selected_stocks)}
             </div>

             <div style="
            color:#9CA3AF;
            font-size:1rem;
             ">
            Selected assets
             </div>

            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("""
<style>
    /* 1. Zentriert die gesamte Tab-Leiste */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        width: 100%;
    }
    
    /* 2. Schriftgröße und Gewicht der Tab-Titel */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 24px; 
        font-weight: bold;
    }
    
    /* 3. Abstand innerhalb der Tabs */
    .stTabs [data-baseweb="tab-list"] button {
        padding: 1.5rem 2rem; 
    }
</style>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "Optimization",
    "Performance",
    "Risk"
])

# Optimization
with tab1:

    with st.container():

        st.subheader(
            "Efficient Frontier"
        )

    st.plotly_chart(
        frontier_fig,
        use_container_width=True
    )
    with st.container():

        st.subheader(
            "Portfolio Allocation"
        )
    st.plotly_chart(
        allocation_fig,
        use_container_width=True
    )
    
    st.dataframe(
        allocation,
        column_config={
            "Company": "Asset",
            "Weight": st.column_config.NumberColumn(
                "Weight",
                format="%.1f %%" 
            )
        },
        hide_index=True,           
        use_container_width=True   
    )

# Performance
with tab2:
    with st.container():

        st.subheader(
            "Cumulative Returns"
        )
    st.plotly_chart(
        cumulative_fig,
        use_container_width=True
    )
    with st.container():


        st.subheader(
            "Rolling Sharpe Ratio"
        )
    st.plotly_chart(
        rolling_fig,
        use_container_width=True
    )
    
# Risk
with tab3:
    with st.container():

        st.subheader(
            "Drawdown Analysis"
        )
    st.plotly_chart(
        drawdown_fig,
        use_container_width=True
    )
    with st.container():

        st.subheader(
            "Correlation Matrix"
        )
    st.plotly_chart(
        correlation_fig,
        use_container_width=True
    )
    