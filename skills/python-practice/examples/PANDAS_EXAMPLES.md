# Pandas Examples

This file contains example data patterns and a reference challenge format for generating practice notebooks.

---

## Example Challenge Format

Use this structure when generating challenges. Each challenge should have:

1. **Header** - Numbered challenge title
2. **Problem statement** - Clear description with expected output
3. **Hidden hint** - Wrapped in `<details>` (easy/medium only)
4. **Data/setup cell** - Code to prepare data for this challenge
5. **Solution placeholder** - Empty cell with `# YOUR SOLUTION HERE`
6. **Hidden solution** - Wrapped in `<details>` with explanation

### Challenge 1

Filter the `stock_returns` DataFrame to show only days where **all stocks** had positive returns.

**Expected output:** A DataFrame with the same columns but fewer rows (only days where every stock was positive).

<details>
<summary>💡 Hint</summary>

Use `.all(axis=1)` to check if all values in a row are True. Combine with a boolean condition `> 0`.

</details>

```python
# Data for this challenge
print(f"stock_returns shape: {stock_returns.shape}")
stock_returns.head()
```

```python
# YOUR SOLUTION HERE
positive_days = None
```

<details>
<summary>✅ Solution</summary>

```python
positive_days = stock_returns[stock_returns.gt(0).all(axis=1)]
```

**Explanation:**
1. `stock_returns.gt(0)` creates a boolean DataFrame (True where return > 0)
2. `.all(axis=1)` returns True for rows where ALL columns are True
3. Using this boolean Series to index `stock_returns` filters to only positive days

</details>

```python
# Verify your solution
print(f"Days with all positive returns: {len(positive_days)}")
positive_days.head()
```

---

## Sample Data Patterns

```python
ser = pd.Series({'AAPL':100,'MSFT':200,'TSLA':50})
df1*ser

ser = pd.Series({'20201201':100,'20201203':200})
df1.mul(ser,axis=0)
```

```python
# Imports
import pandas as pd
ret_dict={'AAPL':-0.01,'MSFT':-0.02,'TSLA':0.015,'LULU':-0.005}
ser=pd.Series(ret_dict)
ser
```


```python
# 2D list or NumPy array

index=['20201201','20201202','20201203','20201204']
columns = ['AAPL','MSFT','TSLA','LULU']

data=[[-0.01,0.03,0.05,0.005],
      [0.015,0.005,-0.05,-0.0025],
      [-0.025,0.0015,-0.02,0.01],
      [-0.03,0.015,0.03,0.01]]

df=pd.DataFrame(data,index=index,columns=columns)
df
```

```python
# NOTE: example categorical data
import pandas as pd
ser = pd.Series({'AAPL':'Tech','XOM':'Energy','MSFT':'Tech','LULU':'Consumer','TSLA':'Consumer','GS':'Financials',
                'BAC':'Financials'})
ser
```

```python
# NOTE: multi-indexing example
import pandas as pd
import numpy as np

univ = ['SPY','TLT','VXX','QQQ']
dates = ['20210105','20210106','20210107','20210108','20210109']

earnings = pd.DataFrame(np.random.randn(5,4), index=dates,columns=univ)
ret_prev = pd.DataFrame(np.random.randn(5,4), index=dates,columns=univ)
pe = pd.DataFrame( np.random.randn(5,4), index=dates,columns=univ)
analyst_est = pd.DataFrame( np.random.randn(5,4), index=dates,columns=univ)

data = {}
data['earnings']=earnings
data['ret_prev']=ret_prev
data['pe']=pe
data['analyst_est']=analyst_est

multi = pd.concat(data)
```
