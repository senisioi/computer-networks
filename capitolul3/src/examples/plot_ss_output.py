import sys
import os
import pandas as pd
import matplotlib.pyplot as plt


in_file = sys.argv[1]

df = pd.read_csv(in_file)
print(df.columns)

df.plot(x='Timestamp', y='cwnd', kind = 'line', yticks=range(df['cwnd'].min(), df['cwnd'].max() + 10, 5))
plt.show()