import csv

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

META_KEYS = ["Name", "Origin", "Self-Descript", "Year", "DOI"]


def distance(row1, row2):
    vec1 = row1["vector"]
    vec2 = row2["vector"]
    assert len(vec1) == len(vec2)
    return sum(abs(vec1[i] - vec2[i]) for i in range(len(vec1)))


def avg_distance(rows):
    distances = []
    for row1 in rows:
        for row2 in rows:
            distances.append(distance(row1, row2))
    return sum(distances) / (len(rows) * len(rows))


def clustering(rows, k):
    arr = np.array([row["vector"] for row in rows])
    kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto").fit(arr)
    #print(kmeans.labels_)
    #print(kmeans.inertia_ / len(rows))
    score = silhouette_score(arr, kmeans.labels_)
    print(f"k={k} gives score {score:.1%}")
    #print(kmeans.cluster_centers_)

    clusters = []
    for c in range(k):
        clusters.append([rows[i] for i in range(len(rows)) if kmeans.labels_[i] == c])

    return clusters


rows = []
with open("Aspects.csv", "r") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        rows.append(row)
        for key in row.keys():
            assert key in META_KEYS or row[key] in ["1", "0", "-1"]

for row in rows:
    vector = []
    for key in row.keys():
        if key in META_KEYS:
            continue
        vector.append(int(row[key]))
    row["vector"] = vector

puck = [row for row in rows if row["Name"] == "PUCK"][0]

print(avg_distance(rows))

#clusters = clustering(rows, 5)
[clustering(rows, k) for k in range(2, 21)]

clusters = clustering(rows, 12)
for cluster in clusters:
    print(f"{avg_distance(cluster):.1f} –", ", ".join([x["Name"] for x in cluster]))
