import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller as ADF



s = pd.Series([1, 2, 3], index = ['a', 'b', 'c'])
d = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns = ['a', 'b', 'c'])
d2 = pd.DataFrame(s)

d.head()
d.describe()

#pd.read_excel('data.xls')
#pd.read_csv('data.csv', encoding = 'utf-8')



ADF(np.random.rand(100))