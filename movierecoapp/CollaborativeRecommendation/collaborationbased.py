from surprise import Dataset, evaluate, Reader, KNNBasic
from surprise.model_selection import cross_validate
from surprise.prediction_algorithms.matrix_factorization import SVD

from DataProcessing.dataprocessing import ratings


print("Training SVD Algorithm")
reader = Reader()
data = Dataset.load_from_df(ratings[['userId', 'movieId', 'rating']], reader)
data.split(n_folds=5)

svd = SVD()
# print(cross_validate(svd, data, measures=['RMSE', 'MAE'], cv=5, verbose=True))
trainset = data.build_full_trainset()
svd.fit(trainset)

def recColl(userid, movieid, gt=None):
    return svd.predict(userid, movieid, gt)


# print(recColl(1,862,3))

