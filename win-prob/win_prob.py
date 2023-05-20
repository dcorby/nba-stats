from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

#X, y = load_iris(return_X_y=True)
#print(X)
#print(y)
# print(X)
# First two
# print(X[:2, :])
import sys
sys.exit()
clf = LogisticRegression(random_state=0).fit(X, y)
clf.predict(X[:2, :])
array([0, 0])
clf.predict_proba(X[:2, :])
clf.score(X, y)

