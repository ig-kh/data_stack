from model import ShapeletRidgeCLF
import pandas as pd
from preprocessing import partial_vectorize, InfiniteImpulseResponseFilter
from sklearn.preprocessing import LabelEncoder
import pickle

if __name__ == "__main__":

    filter = InfiniteImpulseResponseFilter()
    le = LabelEncoder()
    model = ShapeletRidgeCLF()

    train_data = pd.read_csv("../data_ppg/train/ppg_train.csv")
    vec_data = partial_vectorize(train_data, ["Label"])
    X_train = filter(vec_data["seq"])
    y_train = le.fit_transform(vec_data["stat"].ravel())

    model.fit(X_train, y_train)

    model.to_pickle("./checkpoints/model.ckpt")
    with open("./checkpoints/le.ckpt", "wb") as f:
        pickle.dump(le, f)

    print("Done")
