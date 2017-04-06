# -*- coding: utf-8 -*-
import nltk, string
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords
STOPWORDS = stopwords.words("english")

# CORENLP_PATH = '/home/abhishek/tools/corenlp-python'
# import sys
# if not CORENLP_PATH in sys.path:
#     sys.path.append(CORENLP_PATH)

# import jsonrpclib
# from simplejson import loads
# from corenlp import StanfordCoreNLP, batch_parse
# import xmltodict
# from corenlp import *
import jsonrpc
from simplejson import loads


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
                output.append(lemmatizer.lemmatize(pair[0], shortTag))
        return ' '.join(output)

class TextCleaner():
    def __init__(self):
        # self.cachedStopWords = stopwords.words("english")
        self.cachedStopWords = STOPWORDS
        self.cachedPunctuations = set(string.punctuation)
        self.cachedPunctuations.remove('-')
        self.printable = set(string.printable)

    def removeStopWords(self, content):
        removed = ' '.join([word for word in content.split() if word not in self.cachedStopWords])
        return removed

    def removePunctuation(self, text):
        removed = ''.join(ch if ch not in self.cachedPunctuations else ' ' for ch in text)
        # removed = ''.join(ch for ch in text if ch not in self.cachedPunctuations)
        removed = ' '.join(removed.split())
        return removed

    def cleanV0(self, content):
        content = content.lower()
        content = self.removePunctuation(content)
        content = filter(lambda x: x in self.printable, content)
        content = self.removeStopWords(content)

        lemmatizer = LemmatizerWithPOS()
        return lemmatizer.lemmatize(content)

    def clean(self, content):
        content = content.lower()
        content = self.removePunctuation(content)

        content = filter(lambda x: x in self.printable, content)
        # content = self.removeStopWords(content)

        lemmatizer = LemmatizerWithPOS()
        return lemmatizer.lemmatize(content)

if __name__ == '__main__':
    # t = TextCleaner()

    # print t.clean(content)

    # corenlp_dir = "/home/abhishek/tools/corenlp-python/stanford-corenlp-full-2014-08-27/"
    # raw_text_directory = "/home/abhishek/tools/corenlp-python/sample_raw_text/"
    #
    # corenlp = StanfordCoreNLP(corenlp_dir)  # wait a few minutes...
    # corenlp.raw_parse("Parse it")
    #
    # parsed = batch_parse(raw_text_directory, corenlp_dir, raw_output=True)
    # print xmltodict.parse(parsed)

    server = jsonrpc.ServerProxy(jsonrpc.JsonRpc20(), jsonrpc.TransportTcpIp(addr=("127.0.0.1", 8080)))

    result = loads(server.parse("Hello world.  It is so beautiful"))
    print "Result", result