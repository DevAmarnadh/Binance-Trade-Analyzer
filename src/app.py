import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data.loader import (
    load_data,
    clean_data,
    get_account_summary,
    get_trade_summary
)
from analysis.metrics import calculate_metrics
from analysis.ranking import rank_accounts, get_feature_importance
import numpy as np

# Set page config and theme
st.set_page_config(
    page_title="Binance Trade Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional dark color palette
COLORS = {
    'primary': '#00a6fb',      # Bright blue
    'secondary': '#00ff9f',    # Neon green
    'accent': '#ffd700',       # Gold
    'negative': '#ff4b4b',     # Bright red
    'background': '#0a0a0a',   # Near black
    'card_bg': '#1a1a1a',     # Dark gray
    'text': '#ffffff',         # White
    'muted': '#888888',       # Gray
    'border': '#333333'       # Dark border
}

# Custom CSS with dark theme styling
st.markdown(f"""
    <style>
    /* Global Styles */
    .stApp {{
        background-color: {COLORS['background']};
        color: {COLORS['text']};
    }}
    
    /* Metric Cards */
    .metric-card {{
        background-color: {COLORS['card_bg']};
        border-radius: 8px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        border: 1px solid {COLORS['border']};
        transition: transform 0.2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.4);
        border-color: {COLORS['primary']};
    }}
    .metric-value {{
        font-size: 28px;
        font-weight: 600;
        color: {COLORS['primary']};
        margin-bottom: 8px;
        text-shadow: 0 0 10px rgba(0,166,251,0.3);
    }}
    .metric-label {{
        font-size: 14px;
        color: {COLORS['muted']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Headers */
    h1, h2, h3, h4 {{
        color: {COLORS['text']};
        font-weight: 600;
        text-shadow: 0 0 10px rgba(255,255,255,0.1);
    }}
    
    /* Info Cards */
    .info-card {{
        background-color: {COLORS['card_bg']};
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid {COLORS['border']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* Download Section */
    .download-section {{
        background-color: {COLORS['card_bg']};
        border-radius: 8px;
        padding: 1.5rem;
        margin-top: 2rem;
        border: 1px solid {COLORS['border']};
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    ::-webkit-scrollbar-track {{
        background: {COLORS['background']};
    }}
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['border']};
        border-radius: 5px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['primary']};
    }}

    /* DataFrame Styling */
    .dataframe {{
        background-color: {COLORS['card_bg']} !important;
        color: {COLORS['text']} !important;
    }}
    .dataframe th {{
        background-color: {COLORS['card_bg']} !important;
        color: {COLORS['text']} !important;
    }}
    .dataframe td {{
        background-color: {COLORS['card_bg']} !important;
        color: {COLORS['text']} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Update chart configurations
CHART_CONFIG = {
    'paper_bgcolor': COLORS['card_bg'],
    'plot_bgcolor': COLORS['card_bg'],
    'font': {
        'color': COLORS['text'],
        'size': 12
    },
    'xaxis': {
        'gridcolor': COLORS['border'],
        'zerolinecolor': COLORS['border']
    },
    'yaxis': {
        'gridcolor': COLORS['border'],
        'zerolinecolor': COLORS['border']
    },
    'margin': dict(t=40, l=40, r=40, b=40)
}

# Title configuration
TITLE_CONFIG = {
    'font': {
        'color': COLORS['text'],
        'size': 20
    }
}

# Add title and description
st.title("📊 Binance Trade Analyzer")
st.markdown(f"""
<div class="info-card">
    <h4 style="color: {COLORS['primary']};">Analysis Overview</h4>
    <p style="color: {COLORS['text']};">This professional-grade application analyzes historical trade data from Binance accounts over a 90-day period, providing comprehensive insights on:</p>
    <ul style="color: {COLORS['text']};">
        <li><strong>Performance Metrics</strong> (ROI, PnL, Sharpe Ratio)</li>
        <li><strong>Risk Analysis</strong> (Maximum Drawdown, Win Rate)</li>
        <li><strong>Account Rankings</strong></li>
        <li><strong>Trading Patterns</strong></li>
    </ul>
</div>
""", unsafe_allow_html=True)

# File uploader with custom styling
uploaded_file = st.file_uploader(
    "Upload your trade data CSV file",
    type=['csv'],
    help="Upload a CSV file containing your Binance trade history"
)

if uploaded_file is not None:
    with st.spinner('Processing trade data...'):
        # Load and process data
        data = load_data(uploaded_file)
        if data is not None:
            cleaned_data = clean_data(data)
            metrics = calculate_metrics(cleaned_data)
            rankings = rank_accounts(metrics)
            
            # Account Selector
            st.sidebar.header("🔍 Account Filter")
            
            # Add search box
            search_query = st.sidebar.text_input(
                "Search Account ID",
                placeholder="Enter account ID or part of it...",
                help="Search for specific account IDs"
            ).strip()
            
            # Add OR separator with styling
            st.sidebar.markdown(f"""
                <div style="text-align: center; margin: 15px 0;">
                    <div style="display: flex; align-items: center; justify-content: center;">
                        <div style="flex-grow: 1; height: 1px; background-color: {COLORS['border']}"></div>
                        <div style="margin: 0 10px; color: {COLORS['muted']}; font-weight: bold;">OR</div>
                        <div style="flex-grow: 1; height: 1px; background-color: {COLORS['border']}"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Filter accounts based on search
            all_accounts = sorted(metrics.index.unique())
            if search_query:
                filtered_accounts = [acc for acc in all_accounts if str(search_query).lower() in str(acc).lower()]
                if not filtered_accounts:
                    st.sidebar.warning("No accounts found matching your search.")
                    filtered_accounts = all_accounts
            else:
                filtered_accounts = all_accounts
            
            # Account selector with filtered results
            selected_account = st.sidebar.selectbox(
                "Select Account to Analyze",
                ["All Accounts"] + filtered_accounts,
                help="Choose a specific account to view detailed analysis"
            )
            
            # Show number of matching accounts
            if search_query:
                match_count = len(filtered_accounts)
                st.sidebar.info(f"Found {match_count} account{'s' if match_count != 1 else ''} matching your search.")
            
            # Filter data based on selection
            if selected_account != "All Accounts":
                account_metrics = metrics.loc[[selected_account]]
                account_data = cleaned_data[cleaned_data['Port_IDs'] == selected_account]
                account_rankings = rankings[rankings['Port_IDs'] == selected_account]
            else:
                account_metrics = metrics
                account_data = cleaned_data
                account_rankings = rankings
            
            # Summary metrics for selected account or all accounts
            st.header(f"📈 {'Selected Account' if selected_account != 'All Accounts' else 'Overall'} Performance Summary")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_accounts = 1 if selected_account != "All Accounts" else len(metrics)
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-value'>{total_accounts:,}</div>
                        <div class='metric-label'>{'Account' if total_accounts == 1 else 'Total Accounts'}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                avg_roi = account_metrics['roi'].mean()
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-value'>{avg_roi:.2f}%</div>
                        <div class='metric-label'>{'ROI' if total_accounts == 1 else 'Average ROI'}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                total_pnl = account_metrics['total_pnl'].sum()
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-value'>${total_pnl:,.2f}</div>
                        <div class='metric-label'>Total PnL</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                win_rate = account_metrics['win_rate'].mean()
                st.markdown(f"""
                    <div class='metric-card'>
                        <div class='metric-value'>{win_rate:.2f}%</div>
                        <div class='metric-label'>{'Win Rate' if total_accounts == 1 else 'Average Win Rate'}</div>
                    </div>
                """, unsafe_allow_html=True)

            # If a specific account is selected, show its rank
            if selected_account != "All Accounts":
                # Get account details safely
                account_rank_info = rankings[rankings['Port_IDs'] == selected_account]
                
                # Get account metrics regardless of rank
                account_metrics_display = metrics.loc[selected_account]
                
                # Determine rank status
                if not account_rank_info.empty:
                    rank_display = f"{account_rank_info['Rank'].iloc[0]}"
                    score_display = f"{account_rank_info['Score'].iloc[0]:.2f}"
                else:
                    # Calculate score for accounts not in top 20 using the same weights
                    weights = {
                        'roi': 0.3,
                        'total_pnl': 0.2,
                        'sharpe_ratio': 0.2,
                        'win_rate': 0.2,
                        'max_drawdown': 0.1
                    }
                    
                    # Normalize metrics for score calculation
                    normalized_metrics = {}
                    all_metrics = metrics.copy()
                    
                    for metric in weights.keys():
                        if metric == 'max_drawdown':
                            # For max_drawdown, lower is better
                            if all_metrics[metric].max() != all_metrics[metric].min():
                                normalized_metrics[metric] = 1 - (
                                    (account_metrics_display[metric] - all_metrics[metric].min()) /
                                    (all_metrics[metric].max() - all_metrics[metric].min())
                                )
                            else:
                                normalized_metrics[metric] = 0.5
                        else:
                            # For other metrics, higher is better
                            if all_metrics[metric].max() != all_metrics[metric].min():
                                normalized_metrics[metric] = (
                                    (account_metrics_display[metric] - all_metrics[metric].min()) /
                                    (all_metrics[metric].max() - all_metrics[metric].min())
                                )
                            else:
                                normalized_metrics[metric] = 0.5
                    
                    # Calculate weighted score
                    score = sum(weights[metric] * normalized_metrics[metric] for metric in weights.keys())
                    
                    # Calculate relative rank
                    all_scores = pd.concat([
                        rankings['Score'],
                        pd.Series([score], index=['current'])
                    ]).sort_values(ascending=False)
                    relative_rank = all_scores.index.get_loc('current') + 1
                    
                    rank_display = f"#{relative_rank} (Not in Top 20)"
                    score_display = f"{score:.2f}"
                
                st.sidebar.markdown(f"""
                    <div class='info-card'>
                        <h4 style="color: {COLORS['primary']};">Account Details</h4>
                        <p><strong>Overall Rank:</strong> {rank_display}</p>
                        <p><strong>Performance Score:</strong> {score_display}</p>
                        <p><strong>Total Positions:</strong> {account_metrics_display['total_positions']:,}</p>
                        <p><strong>Win Positions:</strong> {account_metrics_display['win_positions']:,}</p>
                        <p><strong>Sharpe Ratio:</strong> {account_metrics_display['sharpe_ratio']:.2f}</p>
                        <p><strong>Max Drawdown:</strong> {account_metrics_display['max_drawdown']:.2f}%</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Add performance comparison with average
                avg_metrics = metrics.mean()
                st.sidebar.markdown(f"""
                    <div class='info-card'>
                        <h4 style="color: {COLORS['primary']};">Performance vs Average</h4>
                        <p><strong>ROI:</strong> {account_metrics_display['roi']:.2f}% vs {avg_metrics['roi']:.2f}%
                            <span style="color: {'green' if account_metrics_display['roi'] > avg_metrics['roi'] else 'red'}">
                                ({'+' if account_metrics_display['roi'] > avg_metrics['roi'] else ''}{(account_metrics_display['roi'] - avg_metrics['roi']):.2f}%)
                            </span>
                        </p>
                        <p><strong>Win Rate:</strong> {account_metrics_display['win_rate']:.2f}% vs {avg_metrics['win_rate']:.2f}%
                            <span style="color: {'green' if account_metrics_display['win_rate'] > avg_metrics['win_rate'] else 'red'}">
                                ({'+' if account_metrics_display['win_rate'] > avg_metrics['win_rate'] else ''}{(account_metrics_display['win_rate'] - avg_metrics['win_rate']):.2f}%)
                            </span>
                        </p>
                        <p><strong>Sharpe Ratio:</strong> {account_metrics_display['sharpe_ratio']:.2f} vs {avg_metrics['sharpe_ratio']:.2f}
                            <span style="color: {'green' if account_metrics_display['sharpe_ratio'] > avg_metrics['sharpe_ratio'] else 'red'}">
                                ({'+' if account_metrics_display['sharpe_ratio'] > avg_metrics['sharpe_ratio'] else ''}{(account_metrics_display['sharpe_ratio'] - avg_metrics['sharpe_ratio']):.2f})
                            </span>
                        </p>
                        <p><strong>Max Drawdown:</strong> {account_metrics_display['max_drawdown']:.2f}% vs {avg_metrics['max_drawdown']:.2f}%
                            <span style="color: {'green' if account_metrics_display['max_drawdown'] < avg_metrics['max_drawdown'] else 'red'}">
                                ({'+' if account_metrics_display['max_drawdown'] > avg_metrics['max_drawdown'] else ''}{(account_metrics_display['max_drawdown'] - avg_metrics['max_drawdown']):.2f}%)
                            </span>
                        </p>
                    </div>
                """, unsafe_allow_html=True)

            # Create tabs for different visualizations
            tabs = st.tabs([
                "📈 Top Performers",
                "🎯 Account Analysis",
                "📊 Trading Patterns",
                "📑 Risk Analysis",
                "🔍 Trade Details"
            ])
            
            with tabs[0]:
                if selected_account != "All Accounts":
                    st.subheader(f"Account Performance Details - {selected_account}")
                else:
                    st.subheader("Top 20 Trading Accounts")
                
                # Add explanation
                st.markdown("""
                    <div class='info-card'>
                        <p>This table shows the top-performing accounts ranked by their overall score. The score is calculated using:</p>
                        <ul>
                            <li>ROI (Return on Investment)</li>
                            <li>Total PnL (Profit and Loss)</li>
                            <li>Sharpe Ratio (Risk-adjusted returns)</li>
                            <li>Maximum Drawdown (Biggest loss from peak)</li>
                            <li>Win Rate (Percentage of profitable trades)</li>
                        </ul>
                        <p>Colors indicate performance: darker colors represent better performance.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Top Performers Tab
                st.dataframe(
                    account_rankings.set_index('Port_IDs').style.format({
                        'Score': '{:.2f}',
                        'ROI (%)': '{:.2f}%',
                        'Total PnL': '${:,.2f}',
                        'Sharpe Ratio': '{:.2f}',
                        'Max Drawdown (%)': '{:.2f}%',
                        'Win Rate (%)': '{:.2f}%'
                    }).background_gradient(
                        subset=['Score'], 
                        cmap='YlOrRd',
                        vmin=0,
                        vmax=1
                    ).background_gradient(
                        subset=['ROI (%)'], 
                        cmap='YlOrRd',
                        vmin=account_rankings['ROI (%)'].min(),
                        vmax=account_rankings['ROI (%)'].max()
                    ).background_gradient(
                        subset=['Total PnL'], 
                        cmap='YlOrRd',
                        vmin=account_rankings['Total PnL'].min(),
                        vmax=account_rankings['Total PnL'].max()
                    ).set_properties(**{
                        'background-color': COLORS['card_bg'],
                        'color': COLORS['text'],
                        'border-color': COLORS['border']
                    }),
                    height=400
                )
                
                st.markdown("""
                    <div class='info-card'>
                        <h4>Understanding the Metrics</h4>
                        <ul>
                            <li><strong>Score:</strong> Overall performance score (0-1)</li>
                            <li><strong>ROI:</strong> Percentage return on investment</li>
                            <li><strong>Total PnL:</strong> Total profit or loss in dollars</li>
                            <li><strong>Sharpe Ratio:</strong> Risk-adjusted return (higher is better)</li>
                            <li><strong>Max Drawdown:</strong> Largest peak-to-trough decline</li>
                            <li><strong>Win Rate:</strong> Percentage of profitable trades</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                
                # Feature Importance with explanation
                st.markdown("""
                    <div class='info-card'>
                        <h4>Ranking Algorithm Weights</h4>
                        <p>This chart shows how different metrics contribute to the overall ranking score. 
                        Higher weights indicate more importance in the final ranking.</p>
                    </div>
                """, unsafe_allow_html=True)
                
                weights = get_feature_importance()
                fig_weights = go.Figure(data=[
                    go.Bar(
                        x=list(weights.values()),
                        y=list(weights.keys()),
                        orientation='h',
                        marker_color=COLORS['primary'],
                        text=[f'{v:.0%}' for v in weights.values()],
                        textposition='auto'
                    )
                ])
                fig_weights.update_layout(
                    **CHART_CONFIG,
                    title={
                        'text': 'Ranking Algorithm Weights',
                        **TITLE_CONFIG
                    },
                    xaxis_title='Weight',
                    yaxis_title='Metric'
                )
                st.plotly_chart(fig_weights, use_container_width=True)
            
            with tabs[1]:
                # Account Analysis Tab
                if selected_account != "All Accounts":
                    st.subheader(f"Account Analysis - {selected_account}")
                else:
                    st.subheader("Overall Account Analysis")
                
                st.markdown("""
                    <div class='info-card'>
                        <h4>Performance Distribution Analysis</h4>
                        <p>Analysis of ROI and PnL distribution:</p>
                        <ul>
                            <li>ROI Distribution shows the return patterns</li>
                            <li>PnL Distribution shows profit/loss patterns</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # ROI Analysis
                    if selected_account != "All Accounts":
                        roi_data = account_metrics[['roi']]
                    else:
                        roi_data = metrics[['roi']]
                    
                    fig_roi = px.histogram(
                        roi_data.reset_index(), 
                        x='roi',
                        nbins=30,
                        labels={'roi': 'ROI (%)', 'count': 'Frequency'},
                        title=f"{'Account' if selected_account != 'All Accounts' else 'Overall'} ROI Distribution",
                        color_discrete_sequence=[COLORS['primary']]
                    )
                    fig_roi.update_layout(**CHART_CONFIG)
                    st.plotly_chart(fig_roi, use_container_width=True)
                
                with col2:
                    # PnL Analysis
                    if selected_account != "All Accounts":
                        pnl_data = account_metrics[['total_pnl']]
                    else:
                        pnl_data = metrics[['total_pnl']]
                    
                    fig_pnl = px.box(
                        pnl_data.reset_index(),
                        y='total_pnl',
                        labels={'total_pnl': 'Total PnL ($)'},
                        title=f"{'Account' if selected_account != 'All Accounts' else 'Overall'} PnL Distribution",
                        points='all',
                        color_discrete_sequence=[COLORS['secondary']]
                    )
                    fig_pnl.update_layout(**CHART_CONFIG)
                    st.plotly_chart(fig_pnl, use_container_width=True)
            
            with tabs[2]:
                # Trading Patterns Tab
                if selected_account != "All Accounts":
                    st.subheader(f"Trading Patterns - {selected_account}")
                else:
                    st.subheader("Overall Trading Patterns")
                
                st.markdown("""
                    <div class='info-card'>
                        <h4>Trading Pattern Analysis</h4>
                        <p>Analysis of trading behavior and performance:</p>
                        <ul>
                            <li>Trading Activity shows position distribution</li>
                            <li>Win/Loss Analysis shows trading success rates</li>
                            <li>Performance Metrics shows key indicators</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Trading Activity
                    if selected_account != "All Accounts":
                        activity_data = account_data.copy()
                    else:
                        activity_data = cleaned_data.copy()
                    
                    # Trading Activity by Type
                    trade_counts = activity_data['trade_type'].value_counts()
                    fig_activity = px.pie(
                        values=trade_counts.values,
                        names=trade_counts.index,
                        title=f"{'Account' if selected_account != 'All Accounts' else 'Overall'} Trading Activity",
                        color_discrete_sequence=px.colors.sequential.Viridis
                    )
                    fig_activity.update_layout(**CHART_CONFIG)
                    st.plotly_chart(fig_activity, use_container_width=True)
                
                with col2:
                    # Win/Loss Analysis
                    if selected_account != "All Accounts":
                        win_loss_data = pd.DataFrame({
                            'Type': ['Winning', 'Losing'],
                            'Trades': [
                                account_metrics.loc[selected_account, 'win_positions'],
                                account_metrics.loc[selected_account, 'total_positions'] - 
                                account_metrics.loc[selected_account, 'win_positions']
                            ]
                        })
                    else:
                        win_loss_data = pd.DataFrame({
                            'Type': ['Winning', 'Losing'],
                            'Trades': [
                                metrics['win_positions'].sum(),
                                metrics['total_positions'].sum() - metrics['win_positions'].sum()
                            ]
                        })
                    
                    fig_winloss = px.bar(
                        win_loss_data,
                        x='Type',
                        y='Trades',
                        title=f"{'Account' if selected_account != 'All Accounts' else 'Overall'} Win/Loss Distribution",
                        color='Type',
                        color_discrete_map={
                            'Winning': COLORS['secondary'],
                            'Losing': COLORS['negative']
                        }
                    )
                    fig_winloss.update_layout(**CHART_CONFIG)
                    st.plotly_chart(fig_winloss, use_container_width=True)
            
            with tabs[3]:
                # Risk Analysis Tab
                if selected_account != "All Accounts":
                    st.subheader(f"Risk Analysis - {selected_account}")
                else:
                    st.subheader("Overall Risk Analysis")
                
                st.markdown("""
                    <div class='info-card'>
                        <h4>Risk Analysis</h4>
                        <p>Analysis of risk metrics and patterns:</p>
                        <ul>
                            <li>Risk Profile shows key risk indicators</li>
                            <li>Risk Distribution shows risk exposure</li>
                            <li>Risk Statistics shows numerical analysis</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Risk Profile
                    if selected_account != "All Accounts":
                        risk_data = account_metrics[['max_drawdown', 'sharpe_ratio', 'win_rate']]
                    else:
                        risk_data = metrics[['max_drawdown', 'sharpe_ratio', 'win_rate']]
                    
                    # Prepare data for radar chart
                    risk_metrics = risk_data.mean()
                    fig_risk = go.Figure()
                    
                    fig_risk.add_trace(go.Scatterpolar(
                        r=[risk_metrics['win_rate'], risk_metrics['sharpe_ratio'], -risk_metrics['max_drawdown']],
                        theta=['Win Rate', 'Sharpe Ratio', 'Max Drawdown'],
                        fill='toself',
                        name='Risk Profile'
                    ))
                    
                    fig_risk.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[-100, 100]
                            )),
                        showlegend=False,
                        title=f"{'Account' if selected_account != 'All Accounts' else 'Overall'} Risk Profile"
                    )
                    st.plotly_chart(fig_risk, use_container_width=True)
                
                with col2:
                    # Risk Statistics
                    if selected_account != "All Accounts":
                        st.markdown(f"""
                            <div class='info-card'>
                                <h4>Risk Statistics</h4>
                                <p><strong>Max Drawdown:</strong> {account_metrics.loc[selected_account, 'max_drawdown']:.2f}%</p>
                                <p><strong>Sharpe Ratio:</strong> {account_metrics.loc[selected_account, 'sharpe_ratio']:.2f}</p>
                                <p><strong>Win Rate:</strong> {account_metrics.loc[selected_account, 'win_rate']:.2f}%</p>
                                <p><strong>Risk-Return Ratio:</strong> {(account_metrics.loc[selected_account, 'roi'] / abs(account_metrics.loc[selected_account, 'max_drawdown'])):.2f}</p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                            <div class='info-card'>
                                <h4>Average Risk Statistics</h4>
                                <p><strong>Max Drawdown:</strong> {metrics['max_drawdown'].mean():.2f}%</p>
                                <p><strong>Sharpe Ratio:</strong> {metrics['sharpe_ratio'].mean():.2f}</p>
                                <p><strong>Win Rate:</strong> {metrics['win_rate'].mean():.2f}%</p>
                                <p><strong>Risk-Return Ratio:</strong> {(metrics['roi'] / abs(metrics['max_drawdown'])).mean():.2f}</p>
                            </div>
                        """, unsafe_allow_html=True)
            
            with tabs[4]:
                # Trade Details Tab
                if selected_account != "All Accounts":
                    st.subheader(f"Trade Details - {selected_account}")
                else:
                    st.subheader("Overall Trade Details")
                
                st.markdown("""
                    <div class='info-card'>
                        <h4>Detailed Trade Analysis</h4>
                        <p>In-depth analysis of trading behavior:</p>
                        <ul>
                            <li>Trade Types shows strategy distribution</li>
                            <li>Position Sizes shows capital allocation</li>
                            <li>Trade Summary shows key statistics</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
                
                # Get trade summary for selected account or all accounts
                if selected_account != "All Accounts":
                    positions, trade_types = get_trade_summary(account_data)
                else:
                    positions, trade_types = get_trade_summary(cleaned_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Trade Types Distribution
                    if selected_account != "All Accounts":
                        trade_dist = account_data['trade_type'].value_counts()
                    else:
                        trade_dist = cleaned_data['trade_type'].value_counts()
                    
                    fig_types = px.pie(
                        values=trade_dist.values,
                        names=trade_dist.index,
                        title=f"{'Account' if selected_account != 'All Accounts' else 'Overall'} Trade Types",
                        color_discrete_sequence=px.colors.sequential.Viridis
                    )
                    fig_types.update_layout(**CHART_CONFIG)
                    st.plotly_chart(fig_types, use_container_width=True)
                
                with col2:
                    # Position Sizes
                    if selected_account != "All Accounts":
                        size_data = account_data.groupby('trade_type')['money_value'].mean()
                    else:
                        size_data = cleaned_data.groupby('trade_type')['money_value'].mean()
                    
                    fig_sizes = px.bar(
                        x=size_data.index,
                        y=size_data.values,
                        title=f"{'Account' if selected_account != 'All Accounts' else 'Overall'} Position Sizes",
                        labels={'x': 'Trade Type', 'y': 'Average Size ($)'},
                        color_discrete_sequence=[COLORS['primary']]
                    )
                    fig_sizes.update_layout(**CHART_CONFIG)
                    st.plotly_chart(fig_sizes, use_container_width=True)
                
                # Trade Summary Table
                st.markdown("""
                    <div class='info-card'>
                        <h4>Trade Summary Statistics</h4>
                        <p>Key trading statistics and metrics:</p>
                    </div>
                """, unsafe_allow_html=True)
                
                summary_df = positions.copy()
                st.dataframe(
                    summary_df.style.format({
                        'total_trades': '{:,.0f}',
                        'winning_trades': '{:,.0f}',
                        'total_value': '${:,.2f}',
                        'win_rate': '{:.2f}%',
                        'avg_trade_size': '${:,.2f}'
                    }).background_gradient(
                        subset=['win_rate'],
                        cmap='YlOrRd'
                    ).set_properties(**{
                        'background-color': COLORS['card_bg'],
                        'color': COLORS['text'],
                        'border-color': COLORS['border']
                    }),
                    height=400
                )
            
            # Download section with custom styling
            st.markdown(f"""
                <div class="download-section">
                    <h4 style="color: {COLORS['primary']};">📥 Download Results</h4>
                    <p style="color: {COLORS['muted']};">Export your analysis results in CSV format for further analysis.</p>
                </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                # Convert rankings to CSV
                csv = account_rankings.to_csv(index=False)
                st.download_button(
                    label="📊 Download Top 20 Rankings",
                    data=csv,
                    file_name="top_20_accounts.csv",
                    mime="text/csv",
                    help="Download detailed metrics for the top 20 performing accounts"
                )
            
            with col2:
                # Convert full metrics to CSV
                full_metrics_csv = account_metrics.to_csv()
                st.download_button(
                    label="📈 Download Full Metrics",
                    data=full_metrics_csv,
                    file_name="all_account_metrics.csv",
                    mime="text/csv",
                    help="Download complete metrics for all accounts"
                ) 