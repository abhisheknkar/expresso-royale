# This file contains code to analyze Cecilia Alm's affect annotated corpus on children's stories.
# We specifically look for non verbal cues in the stories.
import os
from preprocessor import *
import cPickle as pickle

class AlmLine():
    def __init__(self, line, processFlag=True):
        if processFlag:
            self.cleaner = TextCleaner()
        lsplit = line.split()
        self.emotion = self.splitColumn(lsplit[1])
        self.mood = self.splitColumn(lsplit[2])
        self.sentence = ' '.join(lsplit[3:])
        if processFlag:
            self.processedSentence = self.process(self.sentence)
        else:
            self.processedSentence = self.sentence


    def splitColumn(self,column):
        output = [None,None]
        output[0] = column[:column.index(':')]
        output[1] = column[column.index(':')+1:]
        return output

    def process(self, line):
        return self.cleaner.clean(line)

class AlmStory():
    def __init__(self, path):
        # Stores the entire book as a list
        f = open(path,'r')
        self.lines = []
        for line in f.readlines():
            self.lines.append(AlmLine(line))

class AlmData():
    def __init__(self, path=None):
        folder = '../../common-data/datasets/alm/'
        authors = ['HCAndersen', 'Grimms', 'Potter']

        self.almDataset = {}

        for author in authors:
            booksPath = folder + author + '/emmood/'
            books = os.listdir(booksPath)

            for book in books:
                print 'Reading: ', author, book
                self.almDataset[(author,book[:-7])] = AlmStory(booksPath+book)

        self.createRI()

        if path:
            with open(path, 'wb') as outfile:
                pickle.dump(self, outfile)

    def createRI(self):
        self.almRI = {}
        for book in self.almDataset:
            for idx,line in enumerate(self.almDataset[book].lines):
                processed = line.processedSentence
                # processed = line.sentence
                for word in processed.split():
                    if word not in self.almRI:
                        self.almRI[word] = set()
                    self.almRI[word].add((book[0],book[1],idx))

if __name__ == '__main__':
    alm = AlmData('results/alm.pickle')
    # with open('results/alm.pickle', 'rb') as infile:
    #     alm = pickle.load(infile)
    # for word in alm.almRI:
    #     print word, alm.almRI[word]
    # pass