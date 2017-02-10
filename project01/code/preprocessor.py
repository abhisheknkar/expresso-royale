# -*- coding: utf-8 -*-
import nltk, string
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
STOPWORDS = stopwords.words("english")

class LemmatizerWithPOS():
    def get_wordnet_pos(self, treebank_tag):
        if treebank_tag.startswith('J'):
            return wordnet.ADJ
        elif treebank_tag.startswith('V'):
            return wordnet.VERB
        elif treebank_tag.startswith('N'):
            return wordnet.NOUN
        elif treebank_tag.startswith('R'):
            return wordnet.ADV
        else:
            return ''

    def lemmatize(self, text):
        tokens = nltk.word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        lemmatizer = WordNetLemmatizer()

        output = []
        for pair in tagged:
            shortTag = self.get_wordnet_pos(pair[1])

            if shortTag == '':
                output.append(lemmatizer.lemmatize(pair[0]))
            else:
                output.append(lemmatizer.lemmatize(pair[0], self.get_wordnet_pos(pair[1])))
        return ' '.join(output)

class TextCleaner():
    def __init__(self):
        # self.cachedStopWords = stopwords.words("english")
        self.cachedStopWords = STOPWORDS
        self.cachedPunctuations = set(string.punctuation)
        self.cachedPunctuations.remove('-')

    def removeStopWords(self, content):
        removed = ' '.join([word for word in content.split() if word not in self.cachedStopWords])
        return removed

    def removePunctuation(self, text):
        removed = ''.join(ch for ch in text if ch not in self.cachedPunctuations)
        return removed

    def cleanV0(self, content):
        content = content.lower()
        content = self.removePunctuation(content)
        content = self.removeStopWords(content)

        lemmatizer = LemmatizerWithPOS()
        return lemmatizer.lemmatize(content)

    def cleanV1(self, content):
        content = content.lower()

        printable = set(string.printable)
        content = filter(lambda x: x in printable, content)

        content = self.removeStopWords(content)

        lemmatizer = LemmatizerWithPOS()
        return lemmatizer.lemmatize(content)

if __name__ == '__main__':
    t = TextCleaner()

    content = 'i am trying to form sentences'
    print t.clean(content)

