from DataProcessing.dataprocessing import indices, cosine_sim, smd

from Utilities.utility import  weighted_rating


def improved_recommendations(title):
    print('Content based recommendation for ', title)
    idx = indices[title]
    # finding the cosine similarity score of the title.
    sim_scores = list(enumerate(cosine_sim[idx]))
    # sorting according to the scores of term.
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    # taking the first 26 terms.
    sim_scores = sim_scores[1:26]
    # finding the movie indices according to the sim scores.
    movie_indices = [i[0] for i in sim_scores]
    # finding the movies from dataframe.
    movies = smd.iloc[movie_indices][
        ['title', 'vote_count', 'vote_average', 'year']]
    vote_counts = movies[movies['vote_count'].notnull()]['vote_count'].astype(
        'int')
    vote_averages = movies[movies['vote_average'].notnull()][
        'vote_average'].astype('int')
    #calculate mean on vote averages.
    C = vote_averages.mean()
    #take the vote count value of 60th percentile to set the threshold.
    m = vote_counts.quantile(0.60)
    # find the movies according to the vote_count > threshold.
    qualified = movies[
        (movies['vote_count'] >= m) & (movies['vote_count'].notnull()) & (
            movies['vote_average'].notnull())]
    qualified['vote_count'] = qualified['vote_count'].astype('int')
    qualified['vote_average'] = qualified['vote_average'].astype('int')
    # find the weighted rating according to the mean of vote avegrages and vote_count thrshold
    qualified['wr'] = qualified.apply(weighted_rating, args=(m,C), axis=1)
    # sort according to the weighted rating and take the first 10 movies.
    qualified = qualified.sort_values('wr', ascending=False).head(10)
    return qualified

# print(improved_recommendations('The Dark Knight'))

# print(improved_recommendations('Jumanji'))