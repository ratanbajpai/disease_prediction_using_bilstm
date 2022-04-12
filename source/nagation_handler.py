from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
from nltk.corpus import stopwords

sentim_analyzer = SentimentAnalyzer()
stop = set(stopwords.words("english"))


def remove_negative_context_words(text):
    tokens = nltk.word_tokenize(text)
    tokens_neg_marked = nltk.sentiment.util.mark_negation(tokens)
    tokens_without_negative_words = [word for word in tokens_neg_marked if not word.endswith("_NEG")]
    return " ".join(tokens_without_negative_words)


def extract_words_from_text(text):
    tokens = nltk.word_tokenize(text)
    tokens_neg_marked = nltk.sentiment.util.mark_negation(tokens)
    print(f" tokens_neg_marked : {tokens_neg_marked}")
    return [t for t in tokens_neg_marked
             if t.replace("_NEG", "").isalnum() and
             t.replace("_NEG", "") not in stop]


out = remove_negative_context_words("He is not a Canadian or American")
print(f"out : {out}")