import pandas as pd
import unicodedata
import re
from collections import Counter
import math
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
plt.rcParams["font.family"] = "Nirmala UI"
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

#morphological feature extraction function

def extract_morphological_features(review):
    review = unicodedata.normalize("NFC",str(review))
    vowel = 0
    consonant = 0
    chillaksharam = 0
    vowel_sign = 0
    vowels = set("അആഇഈഉഊഋഎഏഐഒഓഔ")
    consonants = set("കഖഗഘങചഛജഝഞടഠഡഢണതഥദധനപഫബഭമയരറലളഴവശഷസഹ")
    chillaksharams = set("ൺൻർൽൾ")
    vowel_signs = set("ാിീുൂൃെേൈൊോൌ")
    for char in review:
        if char in vowels:
            vowel += 1
        elif char in consonants:
            consonant += 1
        elif char in chillaksharams:
            chillaksharam += 1
        elif char in vowel_signs:
            vowel_sign += 1
    return vowel,vowel_sign,consonant,chillaksharam

#extract malayalam words from text

def extract_malayalam_words(text):
    text = unicodedata.normalize("NFC",str(text))
    words = re.findall(r'[\u0D00-\u0D7F]+', text)
    return words


if __name__ == "__main__":
    #Q9 : morphological analysis

    df = pd.read_csv("data/raw/malayalam_movie_reviews_raw.csv")
    features = df["Review"].apply(extract_morphological_features)
    df[["Vowels","Vowel_Signs","Consonants","Chillaksharams"]] = pd.DataFrame(
        features.tolist(),
        index = df.index
    )
    melted_df = pd.melt(
        df,
        id_vars=["Id"],
        value_vars=["Vowels","Consonants","Chillaksharams"],
        var_name="Feature_Type",
        value_name="Feature_Count"
    )
    top_features = melted_df.groupby("Feature_Type")["Feature_Count"].nlargest(5)
    top_indices = top_features.index.get_level_values(1)
    top_reviews = melted_df.loc[top_indices]
    print("\nTop 5 Reviews for each feature : ")
    print(top_reviews[["Id","Feature_Type","Feature_Count"]])
    top_reviews_details = top_reviews.merge(df[["Id","Review"]], on="Id")
    print("\nTop 5 Reviews for each feature with details : ")
    print(top_reviews_details[["Id","Feature_Type","Feature_Count","Review"]])

    #Q10 : Sentiment word frequency analysis

    stop_words = {"ഒരു", "ഈ", "എന്ന", "ആണ്","തന്നെ", "ഞാൻ", "അത്", "ഇത്","ആയിരുന്നു", "എല്ലാം", "എനിക്ക്"}
    positive_words = Counter()
    negative_words = Counter()
    noise_phrase = (
                "പാട്ടുകൾ എല്ലാം തന്നെ വളരെ മോശമായാണ് തോന്നിയത്. "
                "കേൾക്കാൻ ഇമ്പമില്ലാത്ത സംഗീതമായിരുന്നു."       
            )
    for _, row in df.iterrows():
        clean_review = row["Review"].replace(noise_phrase, "")
        words = [
            word for word in extract_malayalam_words(clean_review)
            if word not in stop_words
        ]
        if row["Sentiment"] == 1:
            positive_words.update(words)
        else:
            negative_words.update(words)

    #lod-odds score calculation
    
    total_positive = sum(positive_words.values())
    total_negative = sum(negative_words.values())  
    all_words = set(positive_words) | set(negative_words)
    log_odds = {}
    eligible_words = {word for word in all_words if positive_words[word] + negative_words[word] >= 10}
    for word in eligible_words:
        pos_count = positive_words[word]
        neg_count = negative_words[word]
        positive_odds = (pos_count + 0.5) / (total_positive - pos_count + 0.5)
        negative_odds = (neg_count + 0.5) / (total_negative - neg_count + 0.5)
        score = math.log(positive_odds) - math.log(negative_odds)
        log_odds[word] = score

    #top 12 positive and negative opinion words

    positive_top12 = sorted(log_odds.items(), key=lambda item: item[1], reverse=True)[:12]
    negative_top12 = sorted(log_odds.items(), key=lambda item: item[1])[:12]
    print("\nTop 12 Positive Opinion Words : ")
    for word, score in positive_top12:
        print(word, "Score : ", round(score,3),
              "Positive : ",positive_words[word],
              "Negative : ",negative_words[word])
    print("\nTop 12 Negative Opinion Words : ")
    for word, score in negative_top12:
        print(word, "Score : ",round(score,3),
                "Positive : ",positive_words[word],
                "Negative : ",negative_words[word])
        
    #positive opinion chart

    positive_words_chart = positive_top12[::-1]
    words = [item[0] for item in positive_words_chart]
    scores = [item[1] for item in positive_words_chart]
    fig, ax = plt.subplots(figsize=(12,9))
    y_positions = range(len(words))
    bars = ax.barh(
        y_positions,
        scores,
        color="blue",
        height=0.6
    )
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(words)

    ax.set_xlabel("Log-Odds Score")
    ax.set_ylabel("Positive Opinion Words")
    ax.set_title("Top 12 Positive Opinion Words")

    for bar,score in zip(bars,scores):
        ax.text(
            bar.get_width() + 0.05,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.2f}",
            va="center"
        )
    ax.set_xlim(0,max(scores) + 0.5)
    plt.tight_layout()
    plt.savefig("top12_positive_opinion_words.png",dpi=300,bbox_inches="tight")
    plt.show()

    #negative opinion chart

    negative_words_chart = negative_top12[::-1]
    negative_words_list = [item[0] for item in negative_words_chart]
    negative_scores = [item[1] for item in negative_words_chart]

    fig,ax =plt.subplots(figsize=(12,9))
    y_positions = range(len(negative_words_list))

    bars = ax.barh(
        y_positions,
        negative_scores,
        color="red",
        height=0.6
    )
    ax.set_yticks(list(y_positions))
    ax.set_yticklabels(negative_words_list)

    ax.set_xlabel("Log-Odds Score")
    ax.set_ylabel("Negative Opinion Words")
    ax.set_title("Top 12 Negative Opinion Words")

    for bar,score in zip(bars,negative_scores):
        ax.text(
            bar.get_width() - 0.08,
            bar.get_y() + bar.get_height() / 2,
            f"{score:.2f}",
            va="center",
            ha="right",
            color="black"
        )

    ax.set_xlim(min(negative_scores) - 0.5,0)
    plt.tight_layout()
    plt.savefig("top12_negative_opinion_words.png",dpi=300,bbox_inches="tight")
    plt.show()

    #Q11 : Seaborn Violin plot

    violin_data = df[["Sentiment","Chillaksharams","Vowel_Signs"]].melt(
        id_vars="Sentiment",
        var_name="Feature",
        value_name="Frequency"
    )

    plt.figure(figsize=(10,6))
    sns.violinplot(
        x="Feature",
        y="Frequency",
        hue="Sentiment",
        data=violin_data,
        split=True,
        inner="quart",
        palette={0: "red", 1: "green"}
    )
    legend_elements = [
        Patch(facecolor="red", label="Negative"),
        Patch(facecolor="green", label="Positive")
    ]
    plt.legend(handles=legend_elements, title="Sentiment")
    plt.title("Morphological Feature  Distribution by Sentiment")
    plt.xlabel("Morphological Feature")
    plt.ylabel("Frequency")
    plt.xticks(
        ticks=[0, 1],
        labels=["Chillaksharams", "Vowel Signs"]
    )

    sns.despine()
    plt.tight_layout()
    plt.savefig("q11_morphological_feature_distribution.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()

    #confusion matrix

    X = df["Review"].fillna("").astype(str)
    y = df["Sentiment"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, 
        y, 
        test_size=0.2, 
        random_state=42,
        stratify=y
    )
    tfidf = TfidfVectorizer(
        max_features=5000,
        ngram_range=(1, 2)
    )
    X_train_tfidf = tfidf.fit_transform(X_train)
    X_test_tfidf = tfidf.transform(X_test)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_tfidf, y_train)
    y_pred = model.predict(X_test_tfidf)

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
    plt.figure(figsize=(7, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Negative", "Positive"],
        yticklabels=["Negative", "Positive"]
    )
    plt.title("Sentiment Classification Confusion Matrix")
    plt.xlabel("Predicted Sentiment")
    plt.ylabel("Actual Sentiment")
    sns.despine()
    plt.tight_layout()
    plt.savefig("q11_confusion_matrix.png", dpi=300, bbox_inches="tight")
    plt.show()
    plt.close()