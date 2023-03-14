import warnings
warnings.filterwarnings("ignore")

# =============================================================================
# MANDATORY KNN HW 2
# load data
# =============================================================================
from sklearn.datasets import load_digits
digits = load_digits()

# =============================================================================
# Obtener información sobre el conjunto de datos
# =============================================================================
n_samples = len(digits.images)
n_features = digits.data.shape[1]
n_categories = len(digits.target_names)
# print(digits)
print("Number of samples: %d" % n_samples)
print("Number of features: %d" % n_features)
print("Number of categories: %d" % n_categories)

# =============================================================================
# Statistical support of every feature graphically
# =============================================================================

import matplotlib.pyplot as plt

X, y = load_digits(return_X_y=True) 
plt.boxplot(X)
plt.show()

# =============================================================================
# there are outliers
# =============================================================================
import numpy as np

q1 = np.quantile(X, 0.25, axis = 0)
q3 = np.quantile(X, 0.75, axis = 0)

med = np.median(X)
iqr = q3 - q1

upper_bound = q3+(1.5*iqr)
lower_bound = q1-(1.5*iqr)

#Array with the position of the outlier set to true when the oulier occurs or false when it is not an outlier
array_outliers = []
pos_outliers = []

n_outliers = 0

for line in X:
    count = 0
    flag = False
    for count, value in enumerate(line):
        if value < lower_bound[count] or value > upper_bound[count]:
            flag = True
            n_outliers +=1
        else:
            flag = False
        pos_outliers.append(flag)
    array_outliers.append(pos_outliers)
    pos_outliers = []

# =============================================================================
# true are the outlier and false otherwise
# =============================================================================
print (array_outliers)


# =============================================================================
# Experiments seen in the class
# ============================================================================
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(digits.data, digits.target, test_size=0.1, random_state=42)

# Train the model
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)

# Test the model
y_pred = knn.predict(X_test)

# Print performance metrics
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred))

# =============================================================================
# 4-GridSearchCV() 
# =============================================================================
from sklearn.model_selection import GridSearchCV, LeaveOneOut

param_grid = {'n_neighbors':[1,3]}

miKNNC = KNeighborsClassifier()
miGSCV = GridSearchCV(estimator=miKNNC,
                      scoring='accuracy',
                      param_grid=param_grid,
                      cv=LeaveOneOut(),verbose=4) # 5-fold stratified CV
miGSCV.fit(X_train, y_train)
print("el mejor es:",miGSCV.best_score_)
              
miMejorModelo = miGSCV.best_estimator_
y_pred = miMejorModelo.predict(X_test)
# =============================================================================
# measure success
# =============================================================================

print(100.*sum(y_pred==y_test)/len(y_test))


plt.scatter(y_test,y_pred,s=40)
plt.plot([min(y_test),max(y_test)],[min(y_test),max(y_test)],'k',lw=3)

from sklearn.metrics import r2_score
print(r2_score(y_test,y_pred))
# =============================================================================
# 5
# =============================================================================
from sklearn.preprocessing import StandardScaler

miScaler = StandardScaler()
X_scaled = miScaler.fit_transform(X)
from sklearn.model_selection import StratifiedShuffleSplit

sss = StratifiedShuffleSplit(n_splits = 3, test_size=0.1, random_state=42)

for i, (train_index, test_index) in enumerate(sss.split(X, y)):
    
    X_train = X_scaled[train_index,:]
    y_train = y[train_index]
    
    X_test = X_scaled[test_index,:]
    y_test = y[test_index]
    
# =============================================================================
# importance of crossvalidation
# =============================================================================

from sklearn.model_selection import cross_val_score, StratifiedKFold

# artificially decrease number of samples in class 0
X = digits.data[digits.target != 0]
y = digits.target[digits.target != 0]
y[y == 2] = 0

print('Number of samples in each class:', np.bincount(y))

# Train the model
knn = KNeighborsClassifier(n_neighbors=5)

# cross-validation without stratification
scores = cross_val_score(knn, X, y)
print('Cross-validation scores without stratification:', scores)
print('Mean score without stratification:', np.mean(scores))

# cross-validation with stratification
skf = StratifiedKFold(n_splits=100)
scores = cross_val_score(knn, X, y, cv=skf)
print('Cross-validation scores with stratification:', scores)
print('Mean score with stratification:', np.mean(scores))
      
    
# =============================================================================
# 6 weights
# =============================================================================
from sklearn.model_selection import GridSearchCV

param_grid = {'n_neighbors':[1,3], 
              'weights':['uniform', 'distance'],
              'p':[2,3,4,5]}

miKNNC = KNeighborsClassifier()
miGSCV = GridSearchCV(estimator=miKNNC,
                      param_grid=param_grid,
                      scoring='accuracy',
                      cv=LeaveOneOut(),verbose=4)
miGSCV.fit(X_train, y_train)
print("el mejor es:",miGSCV.best_score_)

              
miMejorModelo = miGSCV.best_estimator_
y_pred = miMejorModelo.predict(X_test)
# =============================================================================
# measure success
# =============================================================================

print(100.*sum(y_pred==y_test)/len(y_test))


plt.scatter(y_test,y_pred,s=40)
plt.plot([min(y_test),max(y_test)],[min(y_test),max(y_test)],'k',lw=3)

from sklearn.metrics import r2_score
print(r2_score(y_test,y_pred))


# =============================================================================
# 7 metric
# =============================================================================
from sklearn.model_selection import GridSearchCV

param_grid = {'n_neighbors':[1,3], 
              'weights':['uniform', 'distance'],
              'p':[2,3,4,5],
              'metric': ['manhattan', 'chebyshev']}

miKNNC = KNeighborsClassifier()
miGSCV = GridSearchCV(estimator=miKNNC,
                      param_grid=param_grid,
                      scoring='accuracy',
                      cv=LeaveOneOut(),verbose=4) 
miGSCV.fit(X_train, y_train)
print("el mejor es:",miGSCV.best_score_)

              
miMejorModelo = miGSCV.best_estimator_
y_pred = miMejorModelo.predict(X_test)
# =============================================================================
# Medimos acierto
# =============================================================================

print(100.*sum(y_pred==y_test)/len(y_test))


plt.scatter(y_test,y_pred,s=40)
plt.plot([min(y_test),max(y_test)],[min(y_test),max(y_test)],'k',lw=3)

from sklearn.metrics import r2_score
print(r2_score(y_test,y_pred))