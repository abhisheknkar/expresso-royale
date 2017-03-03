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
            preprocessedFilepath = self.folderName+'processed/'+self.textName+'_p_'+'.txt'
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
        # self.plot()

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

    def color(self, filepath):
    # This function takes in a piece of text as input and outputs a colored form of the text (with each emotion-
    # keyword colored) as output. Not preprocessing here, since there seem to be no stop words in the NRC corpus
        folderName = filepath[:filepath.rfind('/') + 1]
        textName = filepath[filepath.rfind('/') + 1:-4]
        title = textName
        outpath = folderName + 'colored/' + textName + '.tex'
        f = open(filepath,'r')
        content = f.read()
        f.close()

        positiveSet = set(['trust', 'joy', 'positive'])
        negativeSet = set(['anger', 'disgust', 'fear', 'negative', 'sadness'])
        unsureSet = set(['anticipation', 'surprise'])
        pColor, nColor, uColor, multiColor, noColor = 'green','red','blue','BurntOrange','black'
        lemmatizer = LemmatizerWithPOS()
        # outString = '\\documentclass{article}\n\\usepackage[utf8]{inputenc}\n\\usepackage{color}\n\\title{'+title+'}\n\\begin{document}\n\\maketitle'
        outString = ''

        printable = set(string.printable)
        punctuations = set(string.punctuation)

        lines = content.split('\n')
        numLines = len(lines)
        for idx,line in enumerate(lines):
            if idx%1000==0:
                print idx,'lines processed out of',numLines
            words = line.split()
            for word in words:
                pFlag, nFlag, uFlag = False, False, False
                root = word.lower()
                root = filter(lambda x: x in printable, root)
                root = ''.join(ch for ch in root if ch not in punctuations)
                root = lemmatizer.lemmatize(root)

                if root in self.nrcDict:
                    for emotion in self.nrcDict[root]:
                        pFlag = pFlag or emotion in positiveSet
                        nFlag = nFlag or emotion in negativeSet
                        uFlag = uFlag or emotion in unsureSet

                if pFlag + nFlag + uFlag == 0:
                    color = noColor
                elif pFlag + nFlag + uFlag > 1:   # Multiple contrasting emotions
                    color = multiColor
                else:
                    if pFlag:
                        color = pColor
                    elif nFlag:
                        color = nColor
                    elif uFlag:
                        color = uColor

                word = word.replace('_','')
                if color == 'black':
                    outString += ' ' + word
                else:
                    outString += ' '+'\\textcolor{'+color+'}{'+word+'}'
            outString += '\n\n'
        f = open(outpath, 'w')
        f.write(outString)
        f.close()

if __name__ == '__main__':
    t0 = time.time()

    e = EmotionAnalyzer()
    books = ['PrideAndPrejudice', 'AliceInWonderland', 'AdventuresOfSherlockHolmes']
    # books = ['PrideAndPrejudice_t_']
    for book in books:
        print '\n\nAnalyzing',book
        # e.analyze('../data/Books/'+book+'.txt', window=0.04)
        e.color('../data/Books/'+book+'.txt')

    print 'Time taken: ', time.time()-t0