import pandas as pd

# columns name, description
SOURCE = 'charities.csv'


def load_all_charities():
    return pd.read_csv(SOURCE)[:100]
