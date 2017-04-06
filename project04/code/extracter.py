import sys
sys.path.insert(0,'../../project03-AnalyzeThesaurus/code/')
from analyzer import *

class FeatureExtracter():
    def __init__(self):
        # self.headmatchExact()
        # self.headmatchPartial()
        self.getFeatures()
        self.thesaurus = 1

    def headmatchExact(self):
        # Initializations
        self.thesaurus = Thesaurus()
        self.cue_ = Cue()
        cleaner = TextCleaner()
        lemmatizer = LemmatizerWithPOS()
        self.AlmCueFeatures = {}

        # Load Alm's dataset
        with open('../../project03-AnalyzeThesaurus/code/results/alm.pickle', 'rb') as infile:
            alm = pickle.load(infile)

        # For each cue: get head, look for its occurrence in Alm corpus
        for idx, cue in enumerate(self.thesaurus.emotionCueRI):
            # Get head
            cueSplit = cue.split()
            try:
                root = self.cue_.getRoot(cue)
                rootIndex = cueSplit.index(root)
                rootLem = lemmatizer.lemmatize(root)
            except:
                root, rootIndex, rootLem = None, None, None

            # Look for occurrence in Alm corpus
            if rootLem in alm.almRI:
                locs = alm.almRI[rootLem]   # Get potential matches

                for sentenceID in locs:
                    line = alm.almDataset[(sentenceID[0], sentenceID[1])].lines[sentenceID[2]]  # Get sentence

                    # Find index of words that match root
                    matches = []
                    lineCleanSplit = cleaner.removePunctuation(line.sentence.lower()).split()
                    for idx,word in enumerate(lineCleanSplit):
                        if lemmatizer.lemmatize(word) == rootLem:
                            matches.append(idx)-user

                    # For each such index, get window around it
                    for matchIndex in matches:
                        windowStartIdx = max(matchIndex-rootIndex,0)
                        windowEndIdx = min(matchIndex+len(cueSplit)-rootIndex , len(lineCleanSplit))
                        remCue = cueSplit[0:rootIndex]+cueSplit[rootIndex+1:]
                        remWindow = lineCleanSplit[windowStartIdx:matchIndex]+lineCleanSplit[matchIndex+1:windowEndIdx]
                        if remCue == remWindow:
                            if sentenceID not in self.AlmCueFeatures:
                                self.AlmCueFeatures[sentenceID] = []
                            self.AlmCueFeatures[sentenceID].append((cue,self.thesaurus.emotionCueRI[cue]))
                            # print cue, '\tREMCUE', remCue, '\t', lineCleanSplit[windowStartIdx:windowEndIdx], '\tREMWINDOW:', remWindow
                            # print 'Current matches: ', len(self.AlmCueFeatures)
            if idx % 100 == 0 and idx > 0:
                print 'Processed cues:', idx, 'out of', len(self.thesaurus.emotionCueRI)
        with open('result/AlmCueFeatures.pickle','wb') as fOut:
            pickle.dump(self.AlmCueFeatures, fOut)
        fOut.close()

            # Get the location of the root word match
            # Precision Recall analysis for determining match?

    def headmatchPartial(self, threshold = 0.5):
        # Initializations
        self.thesaurus = Thesaurus()
        self.cue_ = Cue()
        cleaner = TextCleaner()
        lemmatizer = LemmatizerWithPOS()
        self.AlmCueFeatures = {}

        # Load Alm's dataset
        with open('../../project03-AnalyzeThesaurus/code/results/alm.pickle', 'rb') as infile:
            alm = pickle.load(infile)

        # For each cue: get head, look for its occurrence in Alm corpus
        for idx, cue in enumerate(self.thesaurus.emotionCueRI):
            # Get head
            cueSplit = cue.split()
            try:
                root = self.cue_.getRoot(cue)
                rootIndex = cueSplit.index(root)
                rootLem = lemmatizer.lemmatize(root)
            except:
                root, rootIndex, rootLem = None, None, None

            # Look for occurrence in Alm corpus
            if rootLem in alm.almRI:
                locs = alm.almRI[rootLem]   # Get potential matches

                for sentenceID in locs:
                    line = alm.almDataset[(sentenceID[0], sentenceID[1])].lines[sentenceID[2]]  # Get sentence

                    # Find index of words that match root
                    matches = []
                    lineCleanSplit = cleaner.removePunctuation(line.sentence.lower()).split()
                    for idx,word in enumerate(lineCleanSplit):
                        if lemmatizer.lemmatize(word) == rootLem:
                            matches.append(idx)

                    # For each such index, get window around it
                    for matchIndex in matches:
                        windowStartIdx = max(matchIndex-rootIndex,0)
                        windowEndIdx = min(matchIndex+len(cueSplit)-rootIndex , len(lineCleanSplit))
                        remCue = cueSplit[0:rootIndex]+cueSplit[rootIndex+1:]

                        remWindow = lineCleanSplit[windowStartIdx:matchIndex]+lineCleanSplit[matchIndex+1:windowEndIdx]
                        remWindow_lemm = set([lemmatizer.lemmatize(x) for x in remWindow])
                        remCue_lemm = set([lemmatizer.lemmatize(x) for x in remCue])

                        if len(remCue_lemm) == 0 or float(len(remCue_lemm.intersection(remWindow_lemm)))/(len(remCue_lemm)-1e-6)  > threshold:
                        # if remCue == remWindow:
                            if sentenceID not in self.AlmCueFeatures:
                                self.AlmCueFeatures[sentenceID] = []
                            self.AlmCueFeatures[sentenceID].append((cue,self.thesaurus.emotionCueRI[cue]))
                            print cue, '\tREMCUE', remCue, '\t', lineCleanSplit[windowStartIdx:windowEndIdx], '\tREMWINDOW:', remWindow
                            print 'Current matches: ', len(self.AlmCueFeatures)
            if idx % 100 == 0 and idx > 0:
                print 'Processed cues:', idx, 'out of', len(self.thesaurus.emotionCueRI)
        with open('result/AlmCueFeatures.pickle','wb') as fOut:
            pickle.dump(self.AlmCueFeatures, fOut)
        fOut.close()

            # Get the location of the root word match
            # Precision Recall analysis for determining match?

    def getFeatures(self, filePath='result/AlmCueFeatures.pickle'):
        with open('../../project03-AnalyzeThesaurus/code/results/alm.pickle', 'rb') as infile:
            alm = pickle.load(infile)

        fOut = open(filePath, 'rb')
        almCueFeatures = pickle.load(fOut)
        fsave = open(filePath+'.txt','w')

        for sentenceID in almCueFeatures:
            toWrite = ''
            toWrite += alm.almDataset[(sentenceID[0], sentenceID[1])].lines[sentenceID[2]].sentence + '\t'
            for cue in almCueFeatures[sentenceID]:
                toWrite += str(cue) + '\t'
            fsave.write(toWrite+'\n')
        fsave.close()

        # print len(almCueFeatures.keys())
        # count1 = 0
        # count2 = 0
        # for key in almCueFeatures:
        #     for cue in almCueFeatures[key]:
        #         if len(cue[0].split()) > 1:
        #             count1 += 1
        #         else:
        #             count2 += 1
        # print count1, count2

if __name__ == '__main__':
    f = FeatureExtracter()