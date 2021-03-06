# -*- coding: utf-8 -*-
import networkx as nx
import csv
from NRCReader import *
from alm import *
import StanfordDependencies
from bllipparser import RerankingParser
import bllipparser

class Thesaurus():
    def __init__(self):
        self.emotionListPath = '../data/EmotionThesaurus/EmotionList.txt'
        self.thesaurusPath = '../data/EmotionThesaurus/Thesaurus.txt'

        self.emotionSet = self.getEmotionList()
        self.generateCueDictionary()
        self.generateReverseCueIndex()

    def getEmotionList(self):
        f = open(self.emotionListPath,'r')
        emotionList = set()
        for line in f.readlines():
            emotion = line.strip()
            emotionList.add(emotion.lower())
        return emotionList

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

    def generateReverseCueIndex(self,clean=False, toSort=False, toPrint=False):
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
            f1 = open('results/AmbiguousCues.txt','w')
            f2 = open('results/AllCues.txt','w')
            for cue in self.emotionCueRI:
                f2.write(cue + '\t' + ','.join([str(x) for x in self.emotionCueRI[cue]]) + '\n')
                if len(self.emotionCueRI[cue]) > 1:
                    count += 1
                    f1.write(cue + '\t' + ','.join([str(x) for x in self.emotionCueRI[cue]]) + '\n')
            f1.close()
            f2.close()
            print "Cues in the intersection:", count

    def writeCueDictToCSV(self, cueDict, filepath, sumMode=True):
        f1 = open(filepath,'w')
        writer = csv.writer(f1,delimiter=',')
        writer.writerow(['EMOTION', 'PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM', 'CUES OF SUPPRESSED','TOTAL'])

        for emotion in self.emotionCueDict:
            output = [emotion]
            for attribute in ['PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM', 'CUES OF SUPPRESSED']:
                output.append(cueDict[emotion][attribute])
            if sumMode:
                output.append(sum(cueDict[emotion].values()))
            else:
                output.append(cueDict[emotion]['TOTAL'])
            writer.writerow(output)
        f1.close()

class Thesaurus_Contingency():
    def __init__(self):
        self.graphPath = 'results/contingencyGraph.xml'

        self.thesaurus = Thesaurus()
        self.getContingencyList(writeToFile=True)
        self.createContingencyGraph(self.graphPath)

    # Creating Contingency List and Graph
    def getContingencyList(self, writeToFile=False):
        f = open(self.thesaurus.thesaurusPath,'r')
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
                    if potentialTitle.lower() in self.thesaurus.emotionSet and potentialTitle.isupper():
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

class Cue():
    def __init__(self):
        self.rrp = RerankingParser.fetch_and_load('WSJ-PTB3', verbose=True)
        self.sd = StanfordDependencies.get_instance(backend='subprocess')

    def getRoot(self, sentence):
        tree = self.rrp.simple_parse(sentence)

        tokens = self.sd.convert_tree(tree)

        # nbest_list = self.rrp.parse(sentence)
        # tokens = nbest_list[0].ptb_parse.sd_tokens()

        for token in tokens:
            if token.deprel == 'root':
                return token.form

class Thesaurus_CueAnalysis():
    def __init__(self):
        self.thesaurus = Thesaurus()

        self.cue_ = Cue()

        self.cueAnalysis()
        self.morphologicalAnalysis()

        self.LemmatizerEvaluation()
        self.parseTreeEvaluation()

    # General Analysis of Cues
    def cueAnalysis(self, toPrint=True):
        # Objectives:
            # 1: Get total distinct cues per emotion, per cue type
            # 2: Find cues that have multiple emotion types
            # 3: Find fraction of unambiguous cues per emotion, per cue type (make a table)

        # 1: Get total distinct cues per emotion, per cue type
        totalCueDict = {}

        for emotion in self.thesaurus.emotionCueDict:
            totalCueDict[emotion] = {}
            for attribute in ['PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM', 'CUES OF SUPPRESSED']:
                totalCueDict[emotion][attribute] = len(self.thesaurus.emotionCueDict[emotion][attribute])
        self.thesaurus.writeCueDictToCSV(totalCueDict, 'results/CueDistribution_Total.csv')

        # 2: Find cues that have multiple emotion types
        # Initialize the dictionaries
        unambiguousCueDict = {}
        ambiguousCueDict = {}
        for emotion in self.thesaurus.emotionCueDict:
            unambiguousCueDict[emotion] = {}
            ambiguousCueDict[emotion] = {}
            for attribute in ['PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM','CUES OF SUPPRESSED']:
                unambiguousCueDict[emotion][attribute] = 0
                ambiguousCueDict[emotion][attribute] = 0

        for cue in self.thesaurus.emotionCueRI:
            types = self.thesaurus.emotionCueRI[cue]
            if len(types) == 1:
                type = types[0]
                unambiguousCueDict[type[0]][type[1]] += 1
            else:
                for type in types:
                    ambiguousCueDict[type[0]][type[1]] += 1
        self.thesaurus.writeCueDictToCSV(unambiguousCueDict, 'results/CueDistribution_Unambiguous.csv')
        self.thesaurus.writeCueDictToCSV(ambiguousCueDict, 'results/CueDistribution_Ambiguous.csv')

        # 3: Predicting the fraction of ambiguous cues
        ambiguousCueFractionDict = {}
        for emotion in self.thesaurus.emotionCueDict:
            ambiguousCueFractionDict[emotion] = {}
            for attribute in ['PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM', 'CUES OF SUPPRESSED']:
                if ambiguousCueDict[emotion][attribute] == 0:
                    ambiguousCueFractionDict[emotion][attribute] = 0
                else:
                    ambiguousCueFractionDict[emotion][attribute] = float(ambiguousCueDict[emotion][attribute])/totalCueDict[emotion][attribute]
            ambiguousCueFractionDict[emotion]['TOTAL'] = float(sum(ambiguousCueDict[emotion].values()))/sum(totalCueDict[emotion].values())
        self.thesaurus.writeCueDictToCSV(ambiguousCueFractionDict,'results/CueFraction_Ambiguous.csv',sumMode=False)

    # Morphological Analysis of Cues
    def morphologicalAnalysis(self):
        pos = LemmatizerWithPOS()
        posDist = {}
        # for cue in self.emotionCueRI:
        outFile = open('MorphologicalDistributionOfCues.csv','w')
        writer = csv.writer(outFile,delimiter=',')
        writer.writerow(['Emotion','Other','Adjective','Adverb','Noun','Verb','Total Words'])

        for emotion in self.thesaurus.emotionCueDict:
            posDist[emotion] = {}
            # for attribute in self.emotionCueDict[emotion]:
            for attribute in ['PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM', 'CUES OF SUPPRESSED']:
                for cue in self.thesaurus.emotionCueDict[emotion][attribute]:
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

    def parseTreeEvaluation(self):
        f = open('results/NPVP.txt', 'w')
        dist = {}
        for idx, cue in enumerate(self.thesaurus.emotionCueRI):
            parse = self.cue_.rrp.simple_parse(cue)
            tree = bllipparser.Tree(parse)
            subtrees = tree.subtrees()
            currPhrase = []
            for subtree in subtrees:
                if subtree.label == 'S':
                    for subsubtree in subtree:
                        currPhrase.append(subsubtree.label)
                else:
                    currPhrase.append(subtree.label)
            currPhrase= ','.join(currPhrase)
            if currPhrase not in dist:
                dist[currPhrase] = 0
            dist[currPhrase] += 1
            f.write(cue+'\t'+currPhrase+'\n')
            if idx % 100 == 0:
                print idx
        print dist
        f.close()

    # Evaluate Lemmatizer with POS Tagger (on one of Alm's stories)
    def LemmatizerEvaluation(self, numStories=1):
        lemmatizer = LemmatizerWithPOS()
        cleaner = TextCleaner()
        lemmatizer = WordNetLemmatizer()
        lemmatizerWithPOS = LemmatizerWithPOS()

        with open('results/alm.pickle', 'rb') as infile:
            alm = pickle.load(infile)
        count = 0
        f = open('results/lemmatizerEvaluation.txt','w')
        for idx,story in enumerate(alm.almDataset):
            if idx > numStories:
                break
            for line in alm.almDataset[story].lines:
                count += 1
                tokens = nltk.word_tokenize(line.sentence)
                tagged = nltk.pos_tag(tokens)

                for pair in tagged:
                    shortTag = lemmatizerWithPOS.get_wordnet_pos(pair[1])
                    if shortTag == '':
                        output = lemmatizer.lemmatize(pair[0])
                    else:
                        output = lemmatizer.lemmatize(pair[0], shortTag)
                    f.write(pair[0]+'\t'+pair[1]+'\t'+output+'\n')

class Thesaurus_Compare():
    def __init__(self):
        self.thesaurus = Thesaurus()

        self.compareWithEmoLex()

        # self.compareWithAlm_v1()
        self.compareWithAlm_v2()

    # Comparison with EmoLex
    def compareWithEmoLex(self):
        # For all the unigram cues, detect presence in EmoLex and report the comparison of thesaurus and EmoLex labels
        nrcDict = NRCReader('../../common-data/lexicons/NRC_Emotion.txt')
        lemmatizer = LemmatizerWithPOS()
        origExists = 0
        stemExists = 0
        totalUnigrams = 0
        f = open('results/EmoLexComparison.txt','w')

        emoLexExistDict = {}
        emoLexTotalDict = {}
        for emotion in self.thesaurus.emotionCueDict:
            emoLexExistDict[emotion] = {}
            emoLexTotalDict[emotion] = {}
            for attribute in ['PHYSICAL SIGNALS', 'INTERNAL SENSATIONS', 'MENTAL RESPONSES', 'CUES OF ACUTE OR LONG-TERM','CUES OF SUPPRESSED']:
                emoLexExistDict[emotion][attribute] = 0
                emoLexTotalDict[emotion][attribute] = 0

        for cue in self.thesaurus.emotionCueRI:
            cuesplit = cue.split()
            if len(cuesplit) == 1:
                output = ''
                totalUnigrams += 1
                stemmedCue = lemmatizer.lemmatize(cuesplit[0])
                for types in self.thesaurus.emotionCueRI[cue]:
                    emoLexTotalDict[types[0]][types[1]] += 1

                if cuesplit[0] in nrcDict:
                    origExists += 1
                    output += cuesplit[0] + '\t' + str(self.thesaurus.emotionCueRI[cuesplit[0]]) + '\t' + str(nrcDict[cuesplit[0]]) + '\n'
                elif stemmedCue in nrcDict:
                    stemExists += 1
                    output += cuesplit[0] + '/' + stemmedCue + '\t' + str(self.thesaurus.emotionCueRI[cuesplit[0]]) + '\t' + str(nrcDict[stemmedCue]) + '\n'
                if len(output) > 0:
                    f.write(output)
                    for types in self.thesaurus.emotionCueRI[cue]:
                        emoLexExistDict[types[0]][types[1]] += 1
        f.close()

        # print 'Total Unigram Cues: ',totalUnigrams, '\n', 'Words that exist in EmoLex: ',origExists,'\n', 'Lemmatized Words that exist:', stemExists
        self.thesaurus.writeCueDictToCSV(emoLexExistDict,'results/EmoLexExist.csv')
        self.thesaurus.writeCueDictToCSV(emoLexTotalDict,'results/EmoLexTotal.csv')

    # Comparison with Alm
    def compareWithAlm_v1(self, matchThreshold=1):
        # For each cue: 1: process the cue; 2: find the potential sentences from Alm that may match
        # 3: percent match with each potential sentence; 4: for those with match > threshold, store the sentence, cue, label, cueType

        multiWordAnalysisFlag = False
        singleWordAnalysisFlag = True

        with open('results/alm.pickle', 'rb') as infile:
            alm = pickle.load(infile)
        f = open('results/AlmCueCommon.txt','w')
        f1 = open('results/AlmCueCommonUnigrams.txt','w')

        cleaner = TextCleaner()
        numCues = len(self.emotionCueRI)
        wordCount = 0
        wordsInAlm = 0

        unigramsInAlm = 0
        unigramsTotal = 0

        for idx,cue in enumerate(self.emotionCueRI):
            if idx % 100 == 0:
                print idx, 'out of', numCues, 'processed'

            if multiWordAnalysisFlag:
                processedCue = cleaner.clean(cue)
                # processedCue = cleaner.removeStopWords(processedCue)
                words = processedCue.split()
                potentialSentences = set()
                for word in words:
                    wordCount += 1
                    if word in alm.almRI:
                        wordsInAlm += 1
                        [potentialSentences.add(x) for x in alm.almRI[word]]
                for sentenceID in potentialSentences:
                    line = alm.almDataset[(sentenceID[0], sentenceID[1])].lines[sentenceID[2]]
                    storyWords = line.processedSentence.split()
                    common = set(words).intersection(set(storyWords))
                    frac = float(len(common))/len(set(words))
                    if frac >= matchThreshold:
                        f.write(cue+'\t'+str(self.emotionCueRI[cue])+'\t'+line.sentence+'\t'+','.join(line.emotion)+'\n')

            if singleWordAnalysisFlag:
                if len(cue.split()) == 1:
                    unigramsTotal += 1
                    if cue in alm.almRI:
                        unigramsInAlm += 1
                        f1.write(cue + '\n')

        f.close()
        f1.close()
        # print wordCount, wordsInAlm
        print 'Unigrams in Alm: ', unigramsInAlm, 'out of', unigramsTotal

    def compareWithAlm_v2(self):
        cue_ = Cue()
        with open('results/alm.pickle', 'rb') as infile:
            alm = pickle.load(infile)
        f = open('results/rootLemmatized50.txt','w')
        for idx,cue in enumerate(self.thesaurus.emotionCueRI):
            try:
                root = cue_.getRoot(cue)
                f.write(cue + '\t\t' + root + '\n')
                print idx
            except:
                print 'Failed:', idx
                continue

            if idx > 50:
                break
            # cleaner = TextCleaner()
            # processedCue = cleaner.clean(cue)
            # processedCue = cleaner.removeStopWords(processedCue)

class CompareCorpora():
    def __init__(self):
        # WKB, ANEW, EmoLex, Alm
        self.lexicons = {}
        self.lexicons['NRC'] = self.readNRC()
        self.lexicons['WKB'] = self.readWKB()
        self.lexicons['Alm'] = self.readAlm()
        self.lexicons['Thesaurus'] = self.readThesaurus()
        self.intersect()

    def readNRC(self):
        nrcDict = NRCReader('../../common-data/lexicons/NRC_Emotion.txt')
        return set(nrcDict.keys())

    def readWKB(self, filepath = '../../common-data/lexicons/WKB.csv'):
        f = open(filepath, 'r')
        words = set()
        for idx, line in enumerate(f.readlines()):
            if idx == 0:
                continue
            lsplit = line.split(',')
            if len(lsplit) > 1:
                words.add(lsplit[1])
        return words

    def readAlm(self):
        with open('../../project03-AnalyzeThesaurus/code/results/alm.pickle', 'rb') as infile:
            alm = pickle.load(infile)
        return set(alm.almRI.keys())

    def readThesaurus(self):
        thesaurus = Thesaurus()
        words = set()
        for cue in thesaurus.emotionCueRI:
            if len(cue.split()) == 1:
                words.add(cue)
        return words

    def intersect(self):
        self.intersections = {}
        print '\t','\t'.join(self.lexicons.keys())
        for lexicon1 in self.lexicons:
            self.intersections[lexicon1] = {}
            for lexicon2 in self.lexicons:
                common = self.lexicons[lexicon1].intersection(self.lexicons[lexicon2])
                self.intersections[lexicon1][lexicon2] = len(common)
            print lexicon1, self.intersections[lexicon1].values()

if __name__ == '__main__':
    # analyzer = EmotionThesaurusBookAnalyzer()
    # lemmatizer = LemmatizerWithPOS()

    # t = Thesaurus_CueAnalysis()
    compare = CompareCorpora()