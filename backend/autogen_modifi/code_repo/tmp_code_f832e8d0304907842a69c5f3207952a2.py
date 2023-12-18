import pandas as pd
from io import StringIO

# The provided data as a multi-line string
data = """
111,45,female,Caucasian,"$40,000 to $59,999",Married,Yes,LA,South,Won't Create,$100.00,$25.00,$75.00,100,$30.00,12,2,8,4,5,$330.00,31,29%
112,56,female,Caucasian,"$40,000 to $59,999","Single, never married",No,MA,Northeast,Will Create,$200.00,$681.00,$200.00,643,$795.00,5,16,6,25,18,"$2,519.00",70,34%
...
374,45,female,Caucasian,"$40,000 to $59,999","Single, never married",Yes,OH,Midwest,Will Create,$897.00,$988.00,$607.00,514,$243.00,20,13,16,21,9,"$3,249.00",79,25%
"""

# Convert the multi-line string into a StringIO object to simulate a file
data_io = StringIO(data)

# Define the column names based on the provided data
column_names = [
    'ID', 'Age', 'Gender', 'Ethnicity', 'Income', 'Marital_Status', 'Has_Children', 'State', 'Region', 'Intent',
    'Amount1', 'Amount2', 'Amount3', 'Variable1', 'Variable2', 'Variable3', 'Variable4', 'Variable5', 'Variable6',
    'Variable7', 'Total_Amount', 'Variable8', 'Percentage'
]

# Read the data into a pandas DataFrame
df = pd.read_csv(data_io, header=None, names=column_names)

# Convert currency to float and percentage to a ratio
df['Amount1'] = df['Amount1'].replace('[\$,]', '', regex=True).astype(float)
df['Amount2'] = df['Amount2'].replace('[\$,]', '', regex=True).astype(float)
df['Amount3'] = df['Amount3'].replace('[\$,]', '', regex=True).astype(float)
df['Total_Amount'] = df['Total_Amount'].replace('[\$,]', '', regex=True).astype(float)
df['Percentage'] = df['Percentage'].replace('%', '', regex=True).astype(float) / 100

# Display the first few rows of the DataFrame to verify
print(df.head())