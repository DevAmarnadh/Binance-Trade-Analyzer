# README.md

# Binance Trade Analyzer

## Overview

The Binance Trade Analyzer is a Python project designed to analyze historical trade data from Binance accounts. It calculates various financial metrics such as Return on Investment (ROI), Profit and Loss (PnL), Sharpe Ratio, Maximum Drawdown (MDD), and Win Rate. The project also provides a ranked list of the top 20 accounts based on these metrics.

## Features

- Calculate financial metrics for trade data
- Rank accounts based on calculated metrics
- Handle missing values and perform data cleaning
- Unit tests for validation of metrics and data loading

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/binance-trade-analyzer.git
cd binance-trade-analyzer
pip install -r requirements.txt
```

## Usage

To analyze trade data, you can use the functions provided in the `src` directory. Here’s a simple example of how to use the metrics calculation:

```python
from src.analysis.metrics import calculate_metrics
from src.data.loader import load_data

data = load_data('path_to_your_data.csv')
metrics = calculate_metrics(data)
print(metrics)
```

## Running Tests

To ensure everything is working correctly, you can run the unit tests included in the project:

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.