import pickle

from aeon.classification.shapelet_based import ShapeletTransformClassifier
from sklearn.linear_model import RidgeClassifier


class ShapeletRidgeCLF:
    def __init__(
        self,
        base_kwargs={},
        shapelet_kwargs={"n_shapelet_samples": 32, "max_shapelet_length": 128},
    ):
        base_estimator = RidgeClassifier(**base_kwargs)
        self.clf = ShapeletTransformClassifier(
            estimator=base_estimator, **shapelet_kwargs
        )

    def fit(self, X_train, y_train):
        self.clf.fit(X_train, y_train)

    def predict(self, X_test):
        return self.clf.predict(X_test)

    @staticmethod
    def from_pickle(path):
        clf_instance = ShapeletRidgeCLF()

        with open(path, "rb") as f:
            clf_instance.clf = pickle.load(f)

        return clf_instance

    def to_pickle(self, path):
        with open(path, "wb") as f:
            pickle.dump(self.clf, f)
