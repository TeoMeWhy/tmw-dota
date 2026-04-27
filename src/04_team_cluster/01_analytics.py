# %%

import pandas as pd

df = pd.read_csv("team_pacth_hero_stats.csv", sep=";")
df.head()

# %%

df[df['patch']==58].dropna(subset=['team_id'])['qtd_matches_patch'].describe()

df_filter = df[df['patch']==58].dropna(subset=['team_id'])
df_filter = df_filter[df_filter['qtd_matches_patch']>50]
df_filter
# %%

df_analytics = (df_filter.pivot_table(index=['team_id', 'patch'],
                                          columns='hero_id',
                                          values='win_rate_weigth')
                             .reset_index()
                             .fillna(0)
                             )

df_analytics

# %%

features = df_analytics.columns[2:]
X = df_analytics[features]
X

# %%

from sklearn import cluster
import matplotlib.pyplot as plt

cluster_algo = cluster.AgglomerativeClustering(n_clusters=5,
                                               linkage='ward')

cluster_algo.fit(X)

df_analytics['cluster'] = cluster_algo.labels_
df_analytics.groupby('cluster')['team_id'].count()

# %%

df_analytics.groupby('cluster')[features].mean().T.to_csv("cluster_result.csv", sep=";")

# %%

plt.plot(X[1.0], X[2.0], 'o')
plt.grid(True)

# %%


# Initialize 3D plot
fig = plt.figure(figsize=(4,4))
ax = fig.add_subplot(projection='3d')

# Plot points
ax.scatter(X[1.0], X[2.0], X[3.0], c='r', marker='o')

ax.set_xlabel('Hero Id 1')
ax.set_ylabel('Hero Id 2')
ax.set_zlabel('Hero Id 3')

# %%

df_analytics[df_analytics['cluster']==0]['team_id']