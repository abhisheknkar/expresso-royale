from preprocessor import *
from NRCReader import *
import time
import os
import numpy as np
import matplotlib.pyplot as plt


class EmotionAnalyzer():
    def __init__(self):
        self.nrcDict = NRCReader()
        self.emotions = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'negative', 'positive', 'sadness', 'surprise', 'trust']

    def analyze(self, filepath, preprocessed=True, window=0.01):
        # Preprocess the text or read from preprocessed text file
        fileread = False
        cleaner = TextCleaner()
        if preprocessed:
            preprocessedFilepath = filepath[:-4]+'_p_'+'.txt'
            if os.path.exists(preprocessedFilepath):
                fp = open(preprocessedFilepath, 'r')
                processedContent = fp.read()
                fileread = True
                fp.close()

        if not fileread:
            f = open(filepath,'r')
            content = f.read()
            f.close()

            processedContent = cleaner.cleanV1(content)

        if preprocessed and not os.path.exists(preprocessedFilepath):
            with open(preprocessedFilepath,'w') as f:
                f.write(processedContent)
                f.close()

        # Divide the preprocessed text into windows
        processedContent = cleaner.removePunctuation(processedContent)  # Remove punctuations
        contentsplit = processedContent.split()

        if window < 1:
            window = int(window * len(contentsplit))
        numWindows = int(np.ceil(len(contentsplit)/window))+1

        # Create a dictionary to store the emotion intensities
        self.emotionDict = dict((el, np.zeros(numWindows)) for el in self.emotions)

        start = 0
        windowID = 0

        while start < len(contentsplit):
            end = min(start+window, len(contentsplit))
            words = contentsplit[start:end]
            for word in words:
                if word in self.nrcDict:
                    for emotion in self.nrcDict[word]:
                        self.emotionDict[emotion][windowID] += 1

            start = end
            windowID += 1
        self.plot()


    def plot(self):
        x = np.arange(len(self.emotionDict[self.emotions[0]]))
        plt.plot(x,x)
        plt.show()
        # for emotion in self.emotionDict:
        #     plt.plot(x, self.emotionDict[emotion])
        #
        # plt.legend(self.emotions, loc='upper left')
        # plt.show()

if __name__ == '__main__':
    t0 = time.time()

    e = EmotionAnalyzer()
    e.analyze('../data/Books/PrideAndPrejudice.txt', window=0.01)

    print 'Time taken: ', time.time()-t0