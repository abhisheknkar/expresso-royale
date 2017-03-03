class EmotionThesaurusBookAnalyzer():
    def __init__(self):
        self.emotionListPath = '../data/EmotionThesaurus/EmotionList.txt'
        self.thesaurusPath = '../data/EmotionThesaurus/Thesaurus.txt'

        self.emotionSet = self.getEmotionList()
        self.getContingencyList(writeToFile=True)

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
        for line in f.readlines():
            newPageFlag = False
            if ord(line[0]) == 12:
                newPageFlag = True
            lstrip = line.strip()
            if newPageFlag:
                lsplit = lstrip.split()
                if len(lsplit) > 0:
                    potentialTitle = lsplit[0]
                    if potentialTitle.lower() in self.emotionSet and potentialTitle.isupper():
                        title = potentialTitle.lower()
            if lstrip.startswith('MAY ESCALATE TO: '):
                escalateTo = lstrip[lstrip.find(': ')+2:].lower()
                self.contingencyDict[title] = escalateTo.split(', ')
                count += 1
                print count

        if writeToFile:
            f = open('../data/contingency.txt','w')
            for emotion in self.contingencyDict:
                f.write(emotion+' -->  '+','.join(self.contingencyDict[emotion])+'\n')

analyzer = EmotionThesaurusBookAnalyzer()