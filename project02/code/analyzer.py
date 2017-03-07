# -*- coding: utf-8 -*-
import networkx as nx
import numpy as np
from preprocessor import *
import csv

class EmotionThesaurusBookAnalyzer():
    def __init__(self):
        self.emotionListPath = '../data/EmotionThesaurus/EmotionList.txt'
        self.thesaurusPath = '../data/EmotionThesaurus/Thesaurus.txt'
        self.graphPath = '../data/EmotionThesaurus/contingencyGraph.xml'

        self.emotionSet = self.getEmotionList()

        # self.getContingencyList(writeToFile=True)
        # self.createContingencyGraph(self.graphPath)

        self.generateCueDictionary()
        self.generateReverseCueIndex()
        # self.morphologicalAnalysis()

    def getEmotionList(self):
        f = open(self.emotionListPath,'r')
        emotionList = set()
        for line in f.readlines():
            emotion = line.strip()
            emotionList.add(emotion.lower())
        return emotionList

    def getContingencyList(self, writeToFile=False):
        f = open(self.thesaurusPath,'r')
        self.contingencyDict = {}
        title = ''
        count = 0
        incompleteContingency = False
        for line in f.readlines():
            newPageFlag = False
            if ord(line[0]) == 12:
                newPageFlag = True
            lstrip = line.strip()

            if incompleteContingency:
                escalateTo += ' ' + lstrip.lower()
                self.contingencyDict[title] = escalateTo.split(', ')
                incompleteContingency = False
                continue

            if newPageFlag:
                lsplit = lstrip.split()
                if len(lsplit) > 0:
                    potentialTitle = lsplit[0]
                    if potentialTitle.lower() in self.emotionSet and potentialTitle.isupper():
                        title = potentialTitle.lower()
            if lstrip.startswith('MAY ESCALATE TO: '):
                escalateTo = lstrip[lstrip.find(': ')+2:].lower()
                if escalateTo[-1] == ',':
                    incompleteContingency = True
                    continue
                self.contingencyDict[title] = escalateTo.split(', ')
                count += 1

        if writeToFile:
            f = open('../data/EmotionThesaurus/contingency.txt','w')
            for emotion in self.contingencyDict:
                f.write(emotion+' -->  '+','.join(self.contingencyDict[emotion])+'\n')

    def createContingencyGraph0(self, path):
        self.G = nx.DiGraph()
        for emotion1 in self.contingencyDict:
            self.G.add_node(emotion1)
            for emotion2 in self.contingencyDict[emotion1]:
                self.G.add_node(emotion2)
                self.G.add_edge(emotion1,emotion2)
        nx.write_graphml(self.G,path)

    def createContingencyGraph(self, path):
        self.G = nx.DiGraph()
        for emotion1 in self.contingencyDict:
            sequence = [emotion1]
            self.G.add_node(emotion1)
            for emotion2 in self.contingencyDict[emotion1]:
                self.G.add_node(emotion2)
                sequence.append(emotion2)
                self.G.add_edge(sequence[-2],emotion2)
                # if emotion2 == 'satisfaction':
                #     print emotion1,sequence[-2],emotion2
        nx.write_graphml(self.G,path)
        # print nx.cycle_basis(self.G)

    def generateCueDictionary(self):
        f = open(self.thesaurusPath,'r')
        cueAttributes = ['DEFINITION','PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM', 'CUES OF SUPPRESSED', 'WRITER’S TIP']
        title = ''

        self.emotionCueDict = {}
        cueReverseIndex = {}
        count = 0

        for line in f.readlines():
            newPageFlag = False
            if ord(line[0]) == 12:
                newPageFlag = True
            lstrip = line.strip()
            lsplit = lstrip.split()

            if len(lsplit) == 0 or lstrip.startswith('Return to the Table of Contents'):
                continue

            if newPageFlag:
                potentialTitle = lsplit[0]
                if potentialTitle.lower() in self.emotionSet and potentialTitle.isupper():
                    # title = potentialTitle.lower()
                    title = potentialTitle
                    self.emotionCueDict[title] = {}
                    for att in cueAttributes:
                        self.emotionCueDict[title][att] = []

            if len(lsplit[0]) > 1 and lsplit[0].isupper(): # A word larger than 1 char in caps
                cueTypeFlag = [lstrip.startswith(x) for x in cueAttributes]
                whereTrue = [idx for idx,x in enumerate(cueTypeFlag) if x]
                if len(whereTrue) > 0:
                    currAttribute = cueAttributes[whereTrue[0]]  # The current attribute to be considered
                    if currAttribute == 'DEFINITION' or currAttribute == 'WRITER’S TIP': # Store the definition here, since it is in line
                        self.emotionCueDict[title][currAttribute].append(lstrip[lstrip.find(': ') + 2:].lower())

            else:
                self.emotionCueDict[title][currAttribute].append(lstrip)

    def generateReverseCueIndex(self,clean=False, toSort=False, toPrint=True):
        # For each cue, preprocess, sort words alphabetically, store in dictionary
        self.emotionCueRI = {}
        cleaner = TextCleaner()
        for emotion in self.emotionCueDict:
            # for attribute in self.emotionCueDict[emotion]:
            for attribute in ['PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM', 'CUES OF SUPPRESSED']:
                for cue in self.emotionCueDict[emotion][attribute]:
                    if clean:
                        cleanCue = cleaner.clean(cleaner.removePunctuation(cue.lower()))
                    else:
                        cleanCue = cleaner.removePunctuation(cue.lower())
                    if toSort:
                        cleanCue = ' '.join(sorted(list(set(cleanCue.split()))))

                    if cleanCue not in self.emotionCueRI:
                        self.emotionCueRI[cleanCue] = []
                    self.emotionCueRI[cleanCue].append((emotion,attribute))

        # Print the output
        if toPrint:
            print "Total cues:", len(self.emotionCueRI)
            count = 0
            f1 = open('results/intersections.txt','w')
            f2 = open('results/allcues.txt','w')
            for cue in self.emotionCueRI:
                f2.write(cue + '\t' + ','.join([str(x) for x in self.emotionCueRI[cue]]) + '\n')
                if len(self.emotionCueRI[cue]) > 1:
                    count += 1
                    f1.write(cue + '\t' + ','.join([str(x) for x in self.emotionCueRI[cue]]) + '\n')
            f1.close()
            f2.close()
            print "Cues in the intersection:", count

    def morphologicalAnalysis(self):
        pos = LemmatizerWithPOS()
        posDist = {}
        # for cue in self.emotionCueRI:
        outFile = open('morphoDist.csv','w')
        writer = csv.writer(outFile,delimiter=',')
        writer.writerow(['Emotion','Other','Adjective','Adverb','Noun','Verb','Total Words'])

        for emotion in self.emotionCueDict:
            posDist[emotion] = {}
            # for attribute in self.emotionCueDict[emotion]:
            for attribute in ['PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM', 'CUES OF SUPPRESSED']:
                for cue in self.emotionCueDict[emotion][attribute]:
                    try:
                        tokens = nltk.word_tokenize(cue)
                    except:
                        tokens = []
                    tagged = nltk.pos_tag(tokens)
                    for pair in tagged:
                        category = pos.get_wordnet_pos(pair[1])
                        if category not in posDist[emotion]:
                            posDist[emotion][category] = 0
                        posDist[emotion][category] += 1
            totalWords = sum(posDist[emotion].values())
            posDist[emotion] = {k: v*1.0/sum(posDist[emotion].values()) for k, v in posDist[emotion].iteritems()}

            writer.writerow([emotion, posDist[emotion][''], posDist[emotion]['a'], posDist[emotion]['r'], posDist[emotion]['n'], posDist[emotion]['v'], totalWords])
        outFile.close()

analyzer = EmotionThesaurusBookAnalyzer()