import numpy as np
import pandas as pd



# labels = ['face', 'name', 'age', 'email', 'password', 'playlist']
database = pd.read_csv('database.csv')
# database = pd.DataFrame(columns= labels)

def get_database():
    return database




