#!/usr/bin/env python
# coding: utf-8

# In[270]:


import random
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error 
from sklearn.neighbors import KNeighborsRegressor


# In[271]:


train = pd.read_csv('./input/dataset.csv')


# In[272]:


train_temp = train
train_temp = train_temp.dropna()
train_temp.drop(['car', 'motorbike', 'bus', 'truck', 'total'], axis=1, inplace=True)


# In[273]:


train = train.dropna()
train.drop(['car', 'motorbike', 'bus', 'truck'], axis=1, inplace=True)
train['uniqueDate'] = train["Date"].str.replace("-","").astype(int)


# In[274]:


train['Date'] = pd.to_datetime(train['Date'])
train['day'] = train['Date'].dt.weekday


# In[275]:


train['timestamp'] = pd.to_datetime(train['Time'], format= '%H:%M:%S')
train['hour'] = train['timestamp'].dt.hour
train['minute'] = train['timestamp'].dt.minute
train.drop(['Date', 'Time', 'timestamp'], axis=1, inplace=True)


# In[276]:


x = train.drop(['total'], axis=1)
y = train['total']


# In[277]:


model = KNeighborsRegressor(n_neighbors=1)
model.fit(x,y)


# In[278]:


y_pred = model.predict(x)
score=model.score(x,y)
print(score)


# In[279]:


mse =mean_squared_error(y, y_pred)
rmse = math.sqrt(mse)
print("Root Mean Squared Error:", rmse)


# In[280]:


result = train_temp
result['predicted'] = y_pred


# In[281]:


result.to_csv("BTPROJ_predictions_knn.csv")

