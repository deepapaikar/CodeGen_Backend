import pandas as pd
from io import StringIO

# Given data in a string format, which we will convert into a pandas DataFrame
data = """
Strategy,Value 1,Value 2,Value 3,Value 4,Value 5,Value 6,Value 7
Tangent Portfolio,50.6,77.4,22.2,1.95,2.1,0.63,-24.1
Minimum Volatility,7.7,11,16.4,0.53,0.59,0.65,-13.2
Risk Parity,31.8,47.2,20.8,1.43,1.67,0.84,-19.1
Equal Weight,22.3,32.5,18.1,1.2,1.51,0.82,-14.7
A2C,-23.3,-31.1,23.7,-1,-0.74,0.48,-31.4
PPO,3.2,4.4,19.2,0.26,0.21,0.14,-15.1
DDPG,8.5,12.1,21.1,0.49,0.52,0.15,-16.2
SAC,7.9,11.2,17.3,0.53,0.69,0.61,-11.5
TD3,-7.5,-10.4,24.5,-0.2,-0.3,0.47,-25.3
A2C,71.6,113,26.5,2.17,3.93,0.92,-18.2
PPO,37.4,56,21.7,1.57,2.64,0.86,-14.2
DDPG,52.8,81.1,20.3,2.19,4.14,0.93,-12.7
SAC,179,321,43.1,2.58,7.23,0.93,-24.8
TD3,89.2,144.2,26,2.58,5.59,0.95,-16
"""

# Use StringIO to convert the string data into a file-like object so it can be read by pandas
data_io = StringIO(data)

# Read the data into a pandas DataFrame
df = pd.read_csv(data_io)

# Calculate summary statistics for each column (excluding the 'Strategy' column)
summary_statistics = df.describe().transpose()

# Output the summary statistics
print(summary_statistics)