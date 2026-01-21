import pandas as pd
import numpy as np
from pathlib import Path
import collections
import matplotlib.pyplot as plt
import seaborn as sns



def cleaner(path):
    print(path)
    df = pd.read_csv(path)
    print(df)
    df.columns =["name", "blobCount", "count4", "closeCount4", "time", "points"]
    df[['images','palette', 'loc', 'height', 'set', "path"]] = df.name.str.split("/",expand=True)
    df = df.drop(["images", "name"], axis = 1)
    closeEnoughCol = []
    compareArrCol= []
    for p in df.points:
        arrP = p.strip("]").strip("[").split(",")
        compareArrP =  (arrP[0:4]) if len(arrP)>= 4 else arrP
        print(compareArrP)
        if len(compareArrP)>0 and compareArrP[0] != "" :
            closeEnoughCol.append((all([float(d)<5.0 for d in compareArrP])))
        else:
            closeEnoughCol.append(False)
        compareArrCol.append(compareArrP)
    df["closeEnough"] = closeEnoughCol
    df["compareArr"] = compareArrCol
    df_reordered = df.loc[:, ["palette", "loc", "height", "set", 'blobCount', 'closeEnough', 'count4', 'closeCount4', "time", "compareArr", "points", "path"]] 
    df_reordered.to_csv(path)

odd = False
size= False
circ = False
p = Path(".")
# for csv_path in sorted(list(p.glob('src/puck/dotpipeline/pipeline_results/otsu/*.csv'))):
#     cleaner(str(csv_path))
if odd == True:
    framesOdd = []
    for csv_path in sorted(list(p.glob('src/puck/dotpipeline/pipeline_results/otsu/(*, 300, np.float64(0.1))_results.csv'))):
        source = (str(csv_path))
        df= pd.read_csv(source)
        countList= df["blobCount"]
        framesOdd.append(pd.DataFrame({'count': countList,'id': np.repeat(source[43:-12],len(countList))}))
    jointOdd = pd.concat(framesOdd)
    print(jointOdd)
    sns.histplot(data=jointOdd,x="count",hue = "id",discrete=True,kde=True) 
    plt.show()

sizeList = [csv_path for csv_path in sorted(list(p.glob('src/puck/dotpipeline/pipeline_results/otsu/(1, *, np.float64(0.1))_results.csv')))][0::20]


if size == True:
    framesSize = []
    for csv_path in sizeList:
        source = (str(csv_path))
        df= pd.read_csv(source)
        countList= df["blobCount"]
        framesSize.append(pd.DataFrame({'count': countList,'id': np.repeat(source[43:-12],len(countList))}))
    jointSize = pd.concat(framesSize)
    print(jointSize)
    sns.histplot(data=jointSize,x="count",hue = "id",discrete=True,kde=True) 
    plt.show()


if circ == True: 
    framesCirc = []
    for csv_path in sorted(list(p.glob('src/puck/dotpipeline/pipeline_results/otsu/(11, 400, np.float64(*))_results.csv'))):
        source = (str(csv_path))
        df= pd.read_csv(source)
        countList= df["blobCount"]
        framesCirc.append(pd.DataFrame({'count': countList,'id': np.repeat(source[43:-12],len(countList))}))
    jointCirc= pd.concat(framesCirc)
    print(jointCirc)
    sns.histplot(data=jointCirc,x="count",hue = "id",discrete=True,kde=True) 
    plt.show()

# some pattern emerges where about .8 we get really low on circles.

# how much of an impact does x variable have on true vs false for four dots.
# how much of an impact does x variable have on true vs false for close enough

