import pickle

import pandas as pd
from model import ShapeletRidgeCLF
from preprocessing import InfiniteImpulseResponseFilter, partial_vectorize
from sklearn.preprocessing import LabelEncoder

if __name__ == "__main__":

    filter = InfiniteImpulseResponseFilter()
    le = LabelEncoder()
    model = ShapeletRidgeCLF()

    train_data = pd.read_csv("../data_ppg/train/ppg_train.csv")
    if "Unnamed: 0" in train_data.columns:
        train_data = train_data.drop(columns=["Unnamed: 0"])
    vec_data = partial_vectorize(train_data, ["Label"])
    X_train = filter(vec_data["seq"])
    print(X_train.shape)
    y_train = le.fit_transform(vec_data["stat"].ravel())
    print(y_train.shape)

    model.fit(X_train, y_train)

    model.to_pickle("./checkpoints/model.ckpt")
    with open("./checkpoints/le.ckpt", "wb") as f:
        pickle.dump(le, f)

    print("Done")
