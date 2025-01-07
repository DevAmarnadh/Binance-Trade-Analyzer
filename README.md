Binance Trade Analyzer

Overview

The Binance Trade Analyzer is a Python-based tool designed to analyze historical trade data from Binance accounts. It calculates various financial metrics such as:

- Return on Investment (ROI)
- Profit and Loss (PnL)
- Sharpe Ratio
- Maximum Drawdown (MDD)
- Win Rate

Additionally, the tool ranks Binance accounts based on these metrics and provides insights into trading performance. The project also handles missing values, performs data cleaning, and includes unit tests for validation of metrics and data loading.

Features

- Financial Metric Calculation: Computes key financial metrics for trade data.
- Account Ranking: Ranks accounts based on calculated metrics.
- Data Cleaning: Handles missing values and ensures data integrity.
- Unit Tests: Includes tests for validation of metrics and data loading.

Installation

Follow these steps to set up the project locally:

1. Clone the repository:

    git clone https://github.com/DevAmarnadh/Binance-Trade-Analyzer.git

2. Navigate to the project directory:

    cd binance-trade-analyzer

3. Install the required dependencies:

    pip install -r requirements.txt

Usage

To analyze trade data, you can use the functions provided in the src directory. Below is a basic example of how to load data and calculate metrics:

from src.analysis.metrics import calculate_metrics
from src.data.loader import load_data

# Load your historical trade data (CSV file)
data = load_data('path_to_your_data.csv')

# Calculate financial metrics
metrics = calculate_metrics(data)

# Print the calculated metrics
print(metrics)

Running Tests

To ensure that everything is working correctly, you can run the unit tests that are included in the project:

pytest tests/

Contributing

We welcome contributions! If you'd like to contribute to the project, you can:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes.
4. Push to your forked repository.
5. Open a pull request to the main repository.

Feel free to open issues for bug reports or feature suggestions.

License

This project is licensed under the MIT License. See the LICENSE file for more details.
