# Pandas Examples

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
