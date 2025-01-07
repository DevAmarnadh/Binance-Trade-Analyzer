import pandas as pd
import numpy as np

def calculate_roi(trades_df):
    """Calculate Return on Investment for each account"""
    roi_by_account = trades_df.groupby('Port_IDs').agg({
        'realizedProfit': 'sum',
        'quantity': 'sum'
    })
    # Handle zero quantity case
    roi_by_account['roi'] = np.where(
        roi_by_account['quantity'] != 0,
        (roi_by_account['realizedProfit'] / roi_by_account['quantity']) * 100,
        0  # Default to 0 ROI if no quantity traded
    )
    return roi_by_account['roi']

def calculate_pnl(trades_df):
    """Calculate total Profit and Loss for each account"""
    pnl_by_account = trades_df.groupby('Port_IDs')['realizedProfit'].sum()
    return pnl_by_account

def calculate_sharpe_ratio(trades_df, risk_free_rate=0.02):
    """
    Calculate Sharpe Ratio for each account
    risk_free_rate: Annual risk-free rate (default 2%)
    """
    # Calculate daily returns
    trades_df['date'] = trades_df['timestamp'].dt.date
    daily_returns = trades_df.groupby(['Port_IDs', 'date'])['realizedProfit'].sum().reset_index()
    
    # Calculate Sharpe Ratio by account
    sharpe_ratios = {}
    for port_id in daily_returns['Port_IDs'].unique():
        port_returns = daily_returns[daily_returns['Port_IDs'] == port_id]['realizedProfit']
        if len(port_returns) > 1:  # Need at least 2 data points
            daily_rf_rate = (1 + risk_free_rate) ** (1/365) - 1
            excess_returns = port_returns - daily_rf_rate
            std = excess_returns.std()
            if std > 0:  # Avoid division by zero
                sharpe_ratio = np.sqrt(365) * (excess_returns.mean() / std)
            else:
                sharpe_ratio = 0  # Default to 0 if no variation in returns
        else:
            sharpe_ratio = 0  # Default to 0 if insufficient data
        sharpe_ratios[port_id] = sharpe_ratio
    
    return pd.Series(sharpe_ratios)

def calculate_mdd(trades_df):
    """Calculate Maximum Drawdown for each account"""
    mdd_by_account = {}
    
    for port_id in trades_df['Port_IDs'].unique():
        port_trades = trades_df[trades_df['Port_IDs'] == port_id].sort_values('timestamp')
        if len(port_trades) > 0:
            cumulative_returns = (1 + port_trades['realizedProfit']).cumprod()
            if len(cumulative_returns) > 0:
                rolling_max = cumulative_returns.expanding().max()
                drawdowns = cumulative_returns / rolling_max - 1
                mdd = abs(drawdowns.min()) * 100 if len(drawdowns) > 0 else 0
            else:
                mdd = 0
        else:
            mdd = 0
        mdd_by_account[port_id] = mdd
    
    return pd.Series(mdd_by_account)

def calculate_win_rate(trades_df):
    """Calculate Win Rate and related metrics for each account"""
    metrics_by_account = trades_df.groupby('Port_IDs').agg({
        'realizedProfit': lambda x: (x > 0).sum()  # Win positions
    }).join(
        trades_df.groupby('Port_IDs').size().rename('total_positions')  # Total positions
    )
    
    # Calculate win rate, handling division by zero
    metrics_by_account['win_rate'] = np.where(
        metrics_by_account['total_positions'] > 0,
        (metrics_by_account['realizedProfit'] / metrics_by_account['total_positions'] * 100),
        0  # Default to 0% win rate if no positions
    )
    
    return metrics_by_account

def calculate_metrics(trades_df):
    """Calculate all metrics for each account"""
    # Ensure the DataFrame is not empty
    if len(trades_df) == 0:
        raise ValueError("No trade data available for analysis")
        
    metrics = pd.DataFrame({
        'roi': calculate_roi(trades_df),
        'total_pnl': calculate_pnl(trades_df),
        'sharpe_ratio': calculate_sharpe_ratio(trades_df),
        'max_drawdown': calculate_mdd(trades_df)
    })
    
    win_metrics = calculate_win_rate(trades_df)
    metrics['win_rate'] = win_metrics['win_rate']
    metrics['win_positions'] = win_metrics['realizedProfit']
    metrics['total_positions'] = win_metrics['total_positions']
    
    # Replace any remaining NaN values with 0
    metrics = metrics.fillna(0)
    
    return metrics