import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calculate_feature_engineering(data):
    """
    Perform feature engineering on trade data
    """
    df = data.copy()
    
    # Time-based features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    # Calculate trade duration
    df['trade_duration'] = df.groupby(['Port_IDs', 'symbol'])['timestamp'].diff()
    
    # Calculate rolling metrics
    df['rolling_pnl'] = df.groupby('Port_IDs')['realizedProfit'].rolling(
        window=10, min_periods=1
    ).mean().reset_index(0, drop=True)
    
    # Calculate position size relative to account
    df['position_size'] = df['price'] * df['quantity']
    df['relative_position_size'] = df.groupby('Port_IDs')['position_size'].transform(
        lambda x: x / x.mean()
    )
    
    return df

def calculate_risk_metrics(trades):
    """
    Calculate additional risk metrics for trades
    """
    metrics = {}
    
    if len(trades) < 2:
        return {
            'volatility': 0,
            'avg_drawdown': 0,
            'risk_reward_ratio': 0
        }
    
    # Calculate daily returns
    daily_returns = trades.groupby('timestamp')['realizedProfit'].sum().pct_change()
    
    # Volatility (annualized)
    metrics['volatility'] = daily_returns.std() * np.sqrt(252)
    
    # Average drawdown
    cumulative_returns = (1 + daily_returns).cumprod()
    rolling_max = cumulative_returns.expanding().max()
    drawdowns = (cumulative_returns - rolling_max) / rolling_max
    metrics['avg_drawdown'] = abs(drawdowns.mean())
    
    # Risk-reward ratio
    profitable_trades = trades[trades['realizedProfit'] > 0]['realizedProfit']
    losing_trades = abs(trades[trades['realizedProfit'] < 0]['realizedProfit'])
    
    avg_profit = profitable_trades.mean() if len(profitable_trades) > 0 else 0
    avg_loss = losing_trades.mean() if len(losing_trades) > 0 else 0
    
    metrics['risk_reward_ratio'] = avg_profit / avg_loss if avg_loss != 0 else 0
    
    return metrics

def analyze_trading_patterns(trades):
    """
    Analyze trading patterns and behavior
    """
    patterns = {}
    
    # Trading frequency by hour
    patterns['hourly_distribution'] = trades.groupby(
        trades['timestamp'].dt.hour
    )['realizedProfit'].count()
    
    # Trading frequency by day of week
    patterns['daily_distribution'] = trades.groupby(
        trades['timestamp'].dt.dayofweek
    )['realizedProfit'].count()
    
    # Average position holding time
    patterns['avg_holding_time'] = trades.groupby(
        ['Port_IDs', 'symbol']
    )['timestamp'].diff().mean()
    
    return patterns

def generate_summary_report(account_metrics, trade_patterns):
    """
    Generate a summary report of the analysis
    """
    report = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'analysis_period': {
            'start': trade_patterns['timestamp'].min(),
            'end': trade_patterns['timestamp'].max(),
        },
        'overall_metrics': {
            'total_accounts': len(account_metrics),
            'avg_roi': account_metrics['ROI'].mean(),
            'avg_sharpe': account_metrics['Sharpe_Ratio'].mean(),
            'avg_win_rate': account_metrics['win_rate'].mean(),
        },
        'trading_patterns': {
            'most_active_hour': trade_patterns['hourly_distribution'].idxmax(),
            'most_active_day': trade_patterns['daily_distribution'].idxmax(),
            'avg_holding_time': trade_patterns['avg_holding_time'].total_seconds() / 3600  # in hours
        }
    }
    
    return report

# Additional utility functions can be added as needed.