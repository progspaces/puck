import pandas as pd
import numpy as np
from pathlib import Path



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


p = Path(".")
for csv_path in sorted(list(p.glob('src/puck/dotpipeline/pipeline_results/otsu/*.csv'))):
    cleaner(str(csv_path))