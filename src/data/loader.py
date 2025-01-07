import pandas as pd
import numpy as np
import streamlit as st
import json
import ast

REQUIRED_COLUMNS = [
    'Port_IDs', 'timestamp', 'symbol', 'side', 
    'positionSide', 'price', 'quantity', 'realizedProfit'
]

def inspect_dataset(data):
    """
    Inspect the dataset and return basic information
    """
    info = {
        'total_rows': len(data),
        'total_accounts': data['Port_IDs'].nunique(),
        'date_range': (data['timestamp'].min(), data['timestamp'].max()),
        'total_symbols': data['symbol'].nunique(),
        'symbols': data['symbol'].unique(),
        'missing_values': data.isnull().sum()
    }
    return info

def validate_columns(data):
    """
    Validate that all required columns are present in the dataset
    """
    missing_columns = [col for col in REQUIRED_COLUMNS if col not in data.columns]
    if missing_columns:
        # Try to map similar column names
        column_mapping = {
            'Port_IDs': ['port_ids', 'account_id', 'account'],
            'timestamp': ['time', 'date', 'datetime'],
            'symbol': ['asset', 'pair', 'trading_pair'],
            'side': ['trade_side', 'position'],
            'positionSide': ['position_side', 'trade_type'],
            'price': ['trade_price', 'execution_price'],
            'quantity': ['amount', 'size', 'qty'],
            'realizedProfit': ['pnl', 'profit', 'realized_profit']
        }
        
        # Try to find matching columns
        for required_col in missing_columns[:]:
            for alt_name in column_mapping.get(required_col, []):
                if alt_name in data.columns:
                    data.rename(columns={alt_name: required_col}, inplace=True)
                    missing_columns.remove(required_col)
                    break
        
        if missing_columns:
            raise ValueError(
                f"Missing required columns: {', '.join(missing_columns)}. "
                f"Required columns are: {', '.join(REQUIRED_COLUMNS)}"
            )
    return data

def load_data(file_path):
    """
    Load and preprocess Binance trade data
    """
    try:
        # Load the dataset
        data = pd.read_csv(file_path)
        
        # Check if Trade_History column exists
        if 'Trade_History' not in data.columns:
            # Try to find similar column names
            possible_columns = [col for col in data.columns if 'trade' in col.lower() or 'history' in col.lower()]
            if possible_columns:
                # Use the first matching column
                data.rename(columns={possible_columns[0]: 'Trade_History'}, inplace=True)
                st.info(f"Using column '{possible_columns[0]}' as trade history data")
            else:
                # If no trade history column is found, try to use the data as is
                if all(col in data.columns for col in REQUIRED_COLUMNS):
                    st.info("Using direct trade data format")
                    return data
                else:
                    raise ValueError(
                        "Could not find Trade_History column or required trade data columns. "
                        f"Required columns are: {', '.join(REQUIRED_COLUMNS)}"
                    )
        
        # Parse the Trade_History column which contains JSON string
        trades_list = []
        for _, row in data.iterrows():
            # Skip if Trade_History is NaN
            if pd.isna(row['Trade_History']):
                continue
                
            try:
                # First try json.loads
                trades = json.loads(row['Trade_History'])
            except (json.JSONDecodeError, TypeError):
                try:
                    # If that fails, try ast.literal_eval which is safer than eval
                    trades = ast.literal_eval(row['Trade_History'])
                except (ValueError, SyntaxError):
                    # Skip malformed entries
                    st.warning(f"Skipping malformed trade history for Port_ID: {row['Port_IDs']}")
                    continue
            
            # Handle both single trade and list of trades
            if isinstance(trades, dict):
                trades = [trades]  # Convert single trade to list
            elif not isinstance(trades, list):
                continue
                
            for trade in trades:
                if isinstance(trade, dict):  # Ensure trade is a dictionary
                    trade['Port_IDs'] = row['Port_IDs']
                    trades_list.append(trade)
        
        if not trades_list:
            # If no trades were parsed, try to use the data as is
            if all(col in data.columns for col in REQUIRED_COLUMNS):
                st.info("Using direct trade data format")
                return data
            else:
                raise ValueError("No valid trades found in the data")
            
        # Convert list of trades to DataFrame
        data = pd.DataFrame(trades_list)
        
        # Convert timestamp from milliseconds to datetime if 'time' exists
        if 'time' in data.columns:
            data['timestamp'] = pd.to_datetime(data['time'], unit='ms')
            data = data.drop('time', axis=1)
        
        # Display basic information about the dataset
        st.write("Dataset Information:")
        info = inspect_dataset(data)
        st.write(f"Total Rows: {info['total_rows']:,}")
        st.write(f"Total Accounts: {info['total_accounts']:,}")
        st.write(f"Date Range: {info['date_range'][0]} to {info['date_range'][1]}")
        st.write(f"Total Trading Pairs: {info['total_symbols']}")
        
        # Validate and map columns
        data = validate_columns(data)
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

def preprocess_trades(data):
    """
    Preprocess trade data with necessary transformations
    """
    df = data.copy()
    
    try:
        # Create position identifiers
        df['position_type'] = df.apply(
            lambda x: f"{str(x['side']).lower()}_{str(x['positionSide']).lower()}", 
            axis=1
        )
        
        # Convert timestamp to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by Port_IDs and timestamp
        df = df.sort_values(['Port_IDs', 'timestamp'])
        
        # Ensure numeric columns are properly typed
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
        df['realizedProfit'] = pd.to_numeric(df['realizedProfit'], errors='coerce')
        
        # Add trade value column
        df['trade_value'] = df['price'] * df['quantity']
        
        return df
    except Exception as e:
        st.error(f"Error preprocessing trades: {str(e)}")
        st.stop()

def handle_missing_values(data):
    """
    Handle missing values in the dataset
    """
    df = data.copy()
    
    # Report missing values
    missing_values = df.isnull().sum()
    if missing_values.any():
        st.warning("Missing values found in the following columns:")
        for col, count in missing_values[missing_values > 0].items():
            st.write(f"- {col}: {count:,} missing values")
    
    # Fill missing numerical values with 0
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    # Fill missing categorical values with 'Unknown'
    categorical_columns = df.select_dtypes(include=['object']).columns
    df[categorical_columns] = df[categorical_columns].fillna('Unknown')
    
    return df

def classify_trade(row):
    """Classify trade based on side and positionSide"""
    side = row['side'].upper()
    position_side = row.get('positionSide', 'BOTH').upper()
    
    if position_side == 'BOTH':
        return f"{side.lower()}"
    else:
        if side == 'BUY':
            return f"{position_side.lower()}_open" if position_side == 'LONG' else f"{position_side.lower()}_close"
        else:  # SELL
            return f"{position_side.lower()}_close" if position_side == 'LONG' else f"{position_side.lower()}_open"

def clean_data(data):
    """Clean and preprocess the trade data"""
    # Convert timestamp to datetime if it's not already
    if 'timestamp' in data.columns:
        data['timestamp'] = pd.to_datetime(data['timestamp'])
    elif 'time' in data.columns:
        data['timestamp'] = pd.to_datetime(data['time'], unit='ms')
    
    # Classify trades
    if 'side' in data.columns:
        data['trade_type'] = data.apply(classify_trade, axis=1)
    
    # Convert quantity fields
    if 'quantity' in data.columns:
        data['money_value'] = data['quantity']  # Amount in quote currency
    if 'qty' in data.columns:
        data['coin_amount'] = data['qty']  # Amount in base currency
    
    # Calculate trade value in quote currency if not already present
    if 'price' in data.columns and 'coin_amount' in data.columns and 'money_value' not in data.columns:
        data['money_value'] = data['price'] * data['coin_amount']
    
    return data

def get_account_summary(data):
    """
    Get summary statistics for each account
    """
    try:
        summary = data.groupby('Port_IDs').agg({
            'realizedProfit': ['count', 'sum', 'mean'],
            'trade_value': 'sum',
            'price': 'mean'
        })
        
        summary.columns = [
            'total_trades', 'total_pnl', 'avg_profit_per_trade', 
            'total_volume', 'avg_price'
        ]
        
        return summary
    except Exception as e:
        st.error(f"Error generating account summary: {str(e)}")
        st.stop()

def get_trade_summary(data):
    """Get detailed trade summary including position types"""
    summary = pd.DataFrame()
    
    # Group by account and trade type
    trade_types = data.groupby(['Port_IDs', 'trade_type']).agg({
        'realizedProfit': ['count', 'sum'],
        'money_value': 'sum'
    }).round(2)
    
    # Calculate position metrics
    positions = data.groupby('Port_IDs').agg({
        'trade_type': 'count',
        'realizedProfit': lambda x: (x > 0).sum(),
        'money_value': 'sum'
    })
    positions.columns = ['total_trades', 'winning_trades', 'total_value']
    
    # Calculate additional metrics
    positions['win_rate'] = (positions['winning_trades'] / positions['total_trades'] * 100).round(2)
    positions['avg_trade_size'] = (positions['total_value'] / positions['total_trades']).round(2)
    
    return positions, trade_types