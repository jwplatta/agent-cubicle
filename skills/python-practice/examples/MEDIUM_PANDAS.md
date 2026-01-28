## Challenge: Adding Sector Information

Create a new DataFrame called prices_with_sectors that adds a 'Sector' column to each stock's prices. The result should be in long format (also called "tidy" format) with columns: Date, Ticker, Price, Sector.

```python
import pandas as pd
import numpy as np

price_data = {
    'Date': pd.to_datetime(['2025-07-28', '2025-07-29', '2025-07-30', '2025-07-31', '2025-08-01',
                            '2025-09-02', '2025-09-03', '2025-09-04', '2025-09-05', '2025-09-08']),
    'BAC': [47.72, 47.44, 47.45, 46.77, 45.17, 45.36, 45.07, 44.94, 44.44, 45.52,
            48.95, 49.71, 49.84, 49.95, 50.20, 49.88, 49.53, 50.08, 49.51, 49.20],
    'IWM': [222.74, 221.32, 220.19, 218.04, 213.60, 218.38, 219.49, 219.20, 218.49, 218.96,
            230.93, 232.84, 234.49, 234.76, 233.72, 232.46, 232.23, 235.13, 236.31, 236.78],
    'LOW': [227.84, 227.89, 225.31, 221.48, 224.29, 231.63, 235.24, 236.06, 236.33, 238.90,
            256.45, 255.92, 256.25, 255.13, 255.65, 256.32, 258.24, 262.10, 267.45, 270.47],
    'MRK': [82.53, 81.13, 80.26, 76.70, 77.85, 78.41, 79.32, 78.00, 78.91, 79.22,
            83.76, 83.45, 82.54, 81.70, 82.59, 83.93, 82.65, 82.52, 83.17, 82.56],
    'TSM': [241.34, 239.92, 241.49, 240.21, 233.84, 237.61, 231.12, 230.02, 241.21, 240.42,
            234.22, 237.33, 237.90, 236.88, 229.52, 227.06, 230.04, 233.84, 241.99, 245.75]
}

prices = pd.DataFrame(price_data)
prices.set_index('Date', inplace=True)
sectors = pd.Series({
    'BAC': 'Financials',
    'IWM': 'ETF',
    'LOW': 'Consumer',
    'MRK': 'Healthcare',
    'TSM': 'Technology'
})
```

