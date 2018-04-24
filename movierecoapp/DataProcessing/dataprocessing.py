import numpy as np
from ast import literal_eval
import pandas as pd

# columns of movie metadata dataset
from nltk import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from Utilities.utility import filter_keywords, get_director

dtype = {'adult': str,
         'belongs_to_collection': str,
         'budget': int,
         'genres': str,
         'homepage': str,
         'id': int,
         'imdb_id': str,
         'original_language': str,
         'original_title': str,
         'overview': str,
         'popularity': float,
         'poster_path': str,
         'production_companies': str,
         'production_countries': str,
         'release_date': str,
         'revenue': int,
         'runtime': float,
         'spoken_languages': str,
         'status': str,
         'tagline': str,
         'title': str,
         'video': bool,
         'vote_average': float,
         'vote_count': int}

pd.options.mode.chained_assignment = None

md = pd.read_csv('data/movies_metadata.csv', low_memory=False)
links_small = pd.read_csv('data/links_small.csv', low_memory=False)
credits = pd.read_csv('data/credits.csv')
keywords = pd.read_csv('data/keywords.csv')
ratings = pd.read_csv('data/ratings_small.csv', low_memory=False)
id_map = pd.read_csv('data/links_small.csv')[['movieId', 'tmdbId']]

print("Doing data processing")
# converting genres to have only names and dropping genres id.
md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(
    lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
vote_averages = md[md['vote_average'].notnull()]['vote_average'].astype('int')
C = vote_averages.mean()

m = vote_counts.quantile(0.95)

md['year'] = pd.to_datetime(md['release_date'], errors='coerce').apply(
    lambda x: str(x).split('-')[0] if x != np.nan else np.nan)

md = md.drop([19730, 29503, 35587])

md['id'] = md['id'].astype('int')

links_small = links_small[links_small['tmdbId'].notnull()]['tmdbId'].astype(
    'int')

keywords['id'] = keywords['id'].astype('int')
credits['id'] = credits['id'].astype('int')

md = md.merge(credits, on='id')
md = md.merge(keywords, on='id')

#reducing the df 'md' to contain only those values which are present in the links_small dataset.
smd = md[md['id'].isin(links_small)]
# print(smd.shape)

#using literal_eval python parser to parse string to their dataypes as written in the csv files.
smd['cast'] = smd['cast'].apply(literal_eval)
smd['crew'] = smd['crew'].apply(literal_eval)
smd['keywords'] = smd['keywords'].apply(literal_eval)

#storing cast size
smd['cast_size'] = smd['cast'].apply(lambda x: len(x))
smd['crew_size'] = smd['crew'].apply(lambda x: len(x))

#extracting director from dataset and storing it in dataframe. Converting the names to lowercase and removing spaces.
smd['director'] = smd['crew'].apply(get_director)
smd['director'] = smd['director'].astype('str').apply(lambda x: str.lower(x.replace(" ", "")))
smd['director'] = smd['director'].apply(lambda x: [x,x, x])

#extracting the names of cast, keeping the first three casts in dataframe, converting it to lower case and removing spaces.
smd['cast'] = smd['cast'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
smd['cast'] = smd['cast'].apply(lambda x: x[:3] if len(x) >=3 else x)
smd['cast'] = smd['cast'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])

#extracting keywords name attribute from keywords.
smd['keywords'] = smd['keywords'].apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])

#taking the keyword column series, stacking the values according to the index,
# and resetting the first level index to integer and dropping the previous index stored as column due to resetting.
s = smd.apply(lambda x: pd.Series(x['keywords']),axis=1).stack().reset_index(level=1, drop=True)
s.name = 'keyword'
#counting the number of times a keyword appeared.
s = s.value_counts()
#storing only those keywords that appeared more than once.
s = s[s > 1]
#initialzing the stemmer to find the stem word from the keywords. For eg. King from Kings.
stemmer = SnowballStemmer('english')

def filter_keywords(x):
    words = []
    for i in x:
        if i in s:
            words.append(i)
    return words

smd['keywords'] = smd['keywords'].apply(filter_keywords)
smd['keywords'] = smd['keywords'].apply(lambda x: [stemmer.stem(i) for i in x])
smd['keywords'] = smd['keywords'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])

#creating metadata columns as = keywords+cast+director+genres
smd['metadata'] = smd['keywords'] + smd['cast'] + smd['director'] + smd['genres']
smd['metadata'] = smd['metadata'].apply(lambda x: ' '.join(x))

#to create a term vector matrix from the metadata.
count = CountVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
count_matrix = count.fit_transform(smd['metadata'])

#finding the cosine similarity using the term vectors.
cosine_sim = cosine_similarity(count_matrix)

#changing the index to title.
smd = smd.reset_index()
titles = smd['title']
indices = pd.Series(smd.index, index=smd['title'])


def get_md():
    return(md)

