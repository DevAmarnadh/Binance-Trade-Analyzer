import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def normalize_metrics(metrics_df):
    """
    Normalize metrics to a 0-1 scale for fair comparison
    """
    # Create a copy to avoid modifying the original
    df = metrics_df.copy()
    
    # Ensure all values are finite
    df = df.replace([np.inf, -np.inf], 0)
    df = df.fillna(0)
    
    # Columns to normalize
    cols_to_normalize = ['roi', 'total_pnl', 'sharpe_ratio', 'win_rate']
    
    # Handle max_drawdown separately (lower is better)
    mdd = df['max_drawdown']
    if mdd.max() != mdd.min():
        normalized_mdd = 1 - (mdd - mdd.min()) / (mdd.max() - mdd.min())
    else:
        normalized_mdd = pd.Series(1, index=mdd.index)  # All accounts have same MDD
    
    # Initialize normalized DataFrame
    normalized_data = pd.DataFrame(index=df.index)
    
    # Normalize each column separately to handle edge cases
    for col in cols_to_normalize:
        values = df[col]
        if values.max() != values.min():
            normalized_data[col] = (values - values.min()) / (values.max() - values.min())
        else:
            normalized_data[col] = pd.Series(1 if values.iloc[0] > 0 else 0, index=values.index)
    
    # Add normalized MDD
    normalized_data['max_drawdown'] = normalized_mdd
    
    return normalized_data

def get_feature_importance():
    """
    Define feature importance weights for ranking
    """
    weights = {
        'roi': 0.25,           # Return on Investment
        'total_pnl': 0.20,     # Total Profit and Loss
        'sharpe_ratio': 0.20,  # Risk-adjusted returns
        'max_drawdown': 0.15,  # Risk measure
        'win_rate': 0.20       # Consistency measure
    }
    return weights

def rank_accounts(metrics_df, top_n=20):
    """
    Rank accounts based on normalized metrics and weights
    """
    # Normalize metrics
    normalized_metrics = normalize_metrics(metrics_df)
    
    # Get feature weights
    weights = get_feature_importance()
    
    # Calculate weighted scores
    weighted_scores = pd.Series(0, index=metrics_df.index)
    for metric, weight in weights.items():
        weighted_scores += normalized_metrics[metric] * weight
    
    # Create ranking DataFrame
    rankings = pd.DataFrame({
        'Port_IDs': metrics_df.index,
        'Score': weighted_scores,
        'ROI (%)': metrics_df['roi'].round(2),
        'Total PnL': metrics_df['total_pnl'].round(2),
        'Sharpe Ratio': metrics_df['sharpe_ratio'].round(2),
        'Max Drawdown (%)': metrics_df['max_drawdown'].round(2),
        'Win Rate (%)': metrics_df['win_rate'].round(2),
        'Win Positions': metrics_df['win_positions'],
        'Total Positions': metrics_df['total_positions']
    })
    
    # Sort by score and get top N
    rankings = rankings.sort_values('Score', ascending=False).head(top_n)
    rankings['Rank'] = range(1, len(rankings) + 1)
    
    # Reorder columns
    column_order = ['Rank', 'Port_IDs', 'Score', 'ROI (%)', 'Total PnL', 
                   'Sharpe Ratio', 'Max Drawdown (%)', 'Win Rate (%)',
                   'Win Positions', 'Total Positions']
    rankings = rankings[column_order]
    
    return rankings