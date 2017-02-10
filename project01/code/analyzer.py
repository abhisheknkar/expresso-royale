from preprocessor import *
from NRCReader import *
import time
import os
import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

class EmotionAnalyzer():
    def __init__(self):
        self.nrcDict = NRCReader()
        self.emotions = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'negative', 'positive', 'sadness', 'surprise', 'trust']

    def analyze(self, filepath, preprocessed=True, window=0.01):
        # Preprocess the text or read from preprocessed text file
        self.folderName = filepath[:filepath.rfind('/')+1]
        self.textName = filepath[filepath.rfind('/')+1:-4]
        self.window = window
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

        if self.window < 1:
            self.window = int(self.window * len(contentsplit))
        numWindows = int(np.ceil(len(contentsplit)/self.window))+1

        # Create a dictionary to store the emotion intensities
        self.emotionDict = dict((el, np.zeros(numWindows)) for el in self.emotions)

        start = 0
        windowID = 0

        while start < len(contentsplit):
            end = min(start+self.window, len(contentsplit))
            words = contentsplit[start:end]
            for word in words:
                if word in self.nrcDict:
                    for emotion in self.nrcDict[word]:
                        self.emotionDict[emotion][windowID] += 1

            start = end
            windowID += 1
        self.plot()


    def plot(self):
        x = [float(y+1)/len(self.emotionDict[self.emotions[0]])*100 for y in np.arange(len(self.emotionDict[self.emotions[0]]))]
        lines = ["-", "--", "-."]
        linecycler = cycle(lines)

        # colors = ['b','g','r','c','m','y','k']
        # colorcycler = cycle(colors)

        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        for emotion in self.emotionDict:
            plt.plot(x[:-1], self.emotionDict[emotion][0:-1], next(linecycler))

        plt.legend(self.emotions, loc='upper left')
        plt.xlabel('Percentage')
        plt.ylabel('Number of words (window length='+str(self.window)+')')
        plt.title('Variation of emotions over: '+ self.textName)
        # manager = plt.get_current_fig_manager()
        # manager.window.showMaximized()
        plt.show()


        # plt.savefig(self.folderName+self.textName+'.png')

if __name__ == '__main__':
    t0 = time.time()

    e = EmotionAnalyzer()
    books = ['PrideAndPrejudice', 'AliceInWonderland', 'AdventuresOfSherlockHolmes']
    for book in books:
        e.analyze('../data/Books/'+book+'.txt', window=0.04)

    print 'Time taken: ', time.time()-t0