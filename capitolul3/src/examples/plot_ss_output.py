import sys
import os
import pandas as pd
import matplotlib.pyplot as plt


out_dir = '.' #sys.argv[1]
in_file = os.path.join(out_dir, 'socket_stats.csv')

df = pd.read_csv(in_file)
print(df.columns)

df.plot(x='Timestamp', y='cwnd', kind = 'line', yticks=range(df['cwnd'].min(), df['cwnd'].max() + 10, 5))
plt.show()