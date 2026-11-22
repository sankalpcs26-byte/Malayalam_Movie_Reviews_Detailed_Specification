import pandas as pd
import unicodedata

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
if __name__ == "__main__":
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