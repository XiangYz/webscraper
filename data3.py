from sklearn import datasets

iris = datasets.load_iris()
print(iris.data.shape)

from sklearn import svm

clf = svm.LinearSVC()
clf.fit(iris.data, iris.target)
print(clf.predict([[5.0, 3.6, 1.3, 0.25]]))
clf.coef_