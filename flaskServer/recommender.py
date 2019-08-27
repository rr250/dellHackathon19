import pandas as pd
import numpy as np
import pickle

def getItems(price, ram , storage):
    laptop_data=pd.read_csv("data/results.csv")
    model = pickle.load(open("model/kmeans.pkl", "rb"))
    item_class = model.predict(np.array([[-1, -1, ram, -1, -1, -1, price]])).tolist().pop()
    result_data = laptop_data.loc[laptop_data['Class'] == item_class]
    result_data = result_data.loc[laptop_data['Company'] == "Dell"]
    return result_data['Id'][0:3].tolist()

print(getItems(123523, 16, 512))