# %% 
# Imports
import pandas as pd 


# %%
# Constants
gsheetkey = "1TG5w2ETvf9H3eIB1KJG-yDtwizyyYC-lXnq10gt4kdc"
sheet_name = "Murmur - Practice Schedule"


# %%
# DF pull
url=f'https://docs.google.com/spreadsheet/ccc?key={gsheetkey}&output=xlsx'
df = pd.read_excel(url,sheet_name=sheet_name)
print(df)

# %%
