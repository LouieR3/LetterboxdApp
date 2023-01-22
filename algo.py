from surprise import SVD
from surprise import Dataset
from surprise import evaluate, print_perf

# Load the movielens-100k dataset (download it if needed),
data = Dataset.load_builtin('ml-100k')

# Use the famous SVD algorithm.
algo = SVD()

# Evaluate performances of our algorithm on the dataset.
perf = evaluate(algo, data, measures=['RMSE', 'MAE'])

# Print the performances
print_perf(perf)