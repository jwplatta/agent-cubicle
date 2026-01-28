You are helping the user practice pandas with Jupyter notebook challenges.

Invoke the `python-practice` skill to generate practice problems.

When gathering parameters, pre-select **pandas** as the category. Still ask the user about:
- **Subcategory**: Which pandas topic to focus on (Series, DataFrames, time series, groupby, etc.) or a random mix
- **Difficulty**: easy, medium, or hard
- **Number of questions**: How many challenges (default 10)
- **Output directory**: Where to save the notebook
- **Previous exercises folder**: Optional path to avoid repeating exact questions

The skill will:
1. Fetch real market data using yfinance
2. Generate varied question data with random tickers and values
3. Build a notebook with challenges, hidden hints, and solutions
4. Save the notebook to the specified location
