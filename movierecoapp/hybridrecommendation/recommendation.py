from ContentBasedRecommendation.MetadataBased import improved_recommendations
from DataProcessing.dataprocessing import id_map, smd, indices, cosine_sim
from CollaborativeRecommendation.collaborationbased import recColl
from Utilities.utility import convert_int

id_map['tmdbId'] = id_map['tmdbId'].apply(convert_int)
id_map.columns = ['movieId', 'id']
id_map = id_map.merge(smd[['title', 'id']], on='id').set_index('title')

indices_map = id_map.set_index('id')

def hybrid(userId, title):
    print("Hybrid recommendation for ", title)
    idx = indices[title]
    tmdbId = id_map.loc[title]['id']
    # print(idx)
    movie_id = id_map.loc[title]['movieId']

    sim_scores = list(enumerate(cosine_sim[int(idx)]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:26]
    movie_indices = [i[0] for i in sim_scores]

    movies = smd.iloc[movie_indices][
        ['title', 'vote_count', 'vote_average', 'year', 'id']]
    movies['est'] = movies['id'].apply(
        lambda x: recColl(userId, indices_map.loc[x]['movieId']).est)
    movies = movies.sort_values('est', ascending=False)
    return movies.head(10)

print(improved_recommendations('The Dark Knight'))
print('-------------------------------------------------------------------------')
print(hybrid(1, 'The Dark Knight'))



