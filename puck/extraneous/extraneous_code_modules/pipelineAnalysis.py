import pandas as pd
import numpy as np
from pathlib import Path
import collections
import matplotlib.pyplot as plt
import seaborn as sns
import random
from sklearn.preprocessing import OrdinalEncoder
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
from sklearn.naive_bayes import CategoricalNB
from sklearn.metrics import classification_report




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
otsu_corr = False
binary_corr = False
pipeline_corr = False
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

if pipeline_corr == True: 
    df = pd.read_csv("src/puck/dotpipeline/pipeline_results/otsu/(1, 300, np.float64(0.1))_results.csv")
    truncated_df = (df[["palette", "loc", "height", "set", "blobCount", "closeEnough"]])
    df_encoded = pd.get_dummies(truncated_df)
    print(df_encoded)

    matrix = df_encoded.corr()

    plt.figure(figsize=(8,6))
    sns.heatmap(matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Correlation Heatmap")
    plt.show()

## explore if the set has any impact on blob count


otsu_results = pd.read_csv("src/puck/dotpipeline/big_picture/otsu0.json_results.csv")
def otsu_seperator(df):
    df.columns = ["pipeline", "choice", "accuracy", "avg", "median"]
    df["pipeline"]=df["pipeline"].map(lambda x: x.lstrip("(").rstrip("))").replace("np.float64(", ""))
    df[['blur','minarea', 'circ']] = df.pipeline.str.split(",",expand=True)
    df["circ"] = df["circ"].map(lambda x: round(float(x),1))
    return df


otsu_clean = otsu_seperator(otsu_results)
otsu_truc = otsu_clean[["accuracy", "blur", "minarea", "circ"]]

if otsu_corr == True:
    matrix_otsu = otsu_truc.corr()

    plt.figure(figsize=(8,6))
    sns.heatmap(matrix_otsu, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Otsu Correlation Heatmap")
    plt.show()

## explore if accuracy and circularity are tied together


binary_results = pd.read_csv("src/puck/dotpipeline/big_picture/binary0.json_results.csv")
def binary_seperator(df):
    df.columns = ["pipeline", "choice", "accuracy", "avg", "median"]
    df["pipeline"]=df["pipeline"].map(lambda x: x.lstrip("(").replace(")", "").replace("np.float64(", ""))
    df[['blur','minarea', 'circ', 'thresh']] = df.pipeline.str.split(",",expand=True)
    df["circ"] = df["circ"].map(lambda x: round(float(x),1))
    return df

if binary_corr == True:
    binary_clean = binary_seperator(binary_results)
    binary_truc = binary_clean[["accuracy", "blur", "minarea", "circ", "thresh"]]

    matrix_binary = binary_truc.corr()

    plt.figure(figsize=(8,6))
    sns.heatmap(matrix_binary, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
    plt.title("Binary Correlation Heatmap")
    plt.show()

## thresh much more correlated, same with circ


# df = pd.read_csv("src/puck/dotpipeline/pipeline_results/otsu/(1, 300, np.float64(0.1))_results.csv")
# truncated_df = (df[["palette", "loc", "height", "set", "blobCount", "closeEnough"]])
# print(truncated_df)
# df_encoded = pd.get_dummies(truncated_df)
# print(df_encoded)



# framesCirc = []
# for csv_path in sorted(list(p.glob('src/puck/dotpipeline/pipeline_results/otsu/(*, 400, np.float64(*))_results.csv'))):
#         source = (str(csv_path))
#         df= pd.read_csv(source)
#         framesCirc.append(df)
# print(len(framesCirc))
# jointCirc= pd.concat(framesCirc)
# print(jointCirc)
# truncated_df = (jointCirc[["palette", "loc", "height", "set", "blobCount", "closeEnough"]])
# print(truncated_df)
# random.seed(2026)
# adjust  =ran_floats = [random.uniform(-.42,.42) for _ in range(25920)]
# truncated_df["blobCount"] = truncated_df["blobCount"] + adjust
# fig = plt.figure(figsize=(16.9,10))
# ax = fig.gca()
# ax.set_yticks(np.arange(.5, 11.5, 1))
# ax.set_ylim([-.5,11.5])
# sns.swarmplot(data=truncated_df, x="set", y="blobCount", hue= "palette", alpha = .8, size = 1.5)
# plt.legend(loc=2, prop={'size': 20},markerscale=10)
# plt.title("400-Otsu")
# plt.grid()
# plt.show()


framesCirc = []
for csv_path in sorted(list(p.glob('src/puck/dotpipeline/pipeline_results/otsu/(*, *, np.float64(*))_results.csv'))):
        source = (str(csv_path))
        df= pd.read_csv(source)
        framesCirc.append(df)
# print((framesCirc))
jointCirc= pd.concat(framesCirc)
# print(jointCirc)
truncated_df = (jointCirc[["palette", "loc", "height", "set",  "count4"]])
dark_df = truncated_df[truncated_df["palette"]== "dark"]
custom_df = truncated_df[truncated_df["palette"]== "custom"]

dark_df_encoded = pd.get_dummies(dark_df, dtype=int)
print(dark_df_encoded)

X_dark = dark_df_encoded[["loc_davids" , "loc_jack_cole" , "loc_john_honey" , "loc_michaels"  ,"height_high" , "height_medium"  ,"height_short" , "set_A" , "set_B"  ,"set_C" , "set_D" ]]
X_dark = dark_df_encoded[["set_A" , "set_B"  ,"set_C" , "set_D" ]]
# X_custom = custom_df[["set","loc", "height" ]]
y_dark= dark_df_encoded.count4
# y_custom =custom_df.count4




X_train_dark, X_test_dark, y_train_dark, y_test_dark = train_test_split(X_dark , y_dark, test_size=0.33, random_state=2026)

logreg = LogisticRegression(random_state=2026)

# # fit the model with data
logreg.fit(X_train_dark, y_train_dark)

y_pred_dark = logreg.predict(X_test_dark)


# clf_dark = CategoricalNB()
# clf_dark.fit(X_train_dark, y_train_dark)
# y_pred_dark = clf_dark.predict(X_test_dark)
cnf_matrix_dark = metrics.confusion_matrix(y_test_dark,y_pred_dark)
print(cnf_matrix_dark)



# X_train_custom, X_test_custom, y_train_custom, y_test_custom= train_test_split(X_encoded_custom , y_custom, test_size=0.33, random_state=2026)
# clf_custom= CategoricalNB()
# clf_custom.fit(X_train_custom, y_train_custom)
# y_pred_custom= clf_custom.predict(X_test_custom)
# cnf_matrix_custom = metrics.confusion_matrix(y_test_custom,y_pred_custom)
# print(cnf_matrix_custom)

fig, ax = plt.subplots()
# create heatmap
sns.heatmap(pd.DataFrame(cnf_matrix_dark), annot=True, cmap="YlGnBu" ,fmt='g')
ax.xaxis.set_label_position("top")
plt.tight_layout()
plt.title('Confusion matrix dark')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
plt.show()

target_names = ['0', '1']
print(classification_report(y_test_dark, y_pred_dark, target_names=target_names))


