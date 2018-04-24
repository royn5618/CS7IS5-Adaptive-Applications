import numpy as np

def weighted_rating(x, m, C):
    v = x['vote_count']
    R = x['vote_average']
    return (v/(v+m) * R) + (m/(m+v) * C)

def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return i['name']
    return np.nan

def filter_keywords(x, s):
    words = []
    for i in x:
        if i in s:
            words.append(i)
    return words

def convert_int(x):
    try:
        return int(x)
    except:
        return np.nan
