import networkx as nx

class EmotionThesaurusBookAnalyzer():
    def __init__(self):
        self.emotionListPath = '../data/EmotionThesaurus/EmotionList.txt'
        self.thesaurusPath = '../data/EmotionThesaurus/Thesaurus.txt'
        self.graphPath = '../data/EmotionThesaurus/contingencyGraph.xml'

        self.emotionSet = self.getEmotionList()
        self.getContingencyList(writeToFile=True)
        self.createContingencyGraph(self.graphPath)

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


def find_all_cycles(G, source=None, cycle_length_limit=None):
    """forked from networkx dfs_edges function. Assumes nodes are integers, or at least
    types which work with min() and > ."""
    if source is None:
        # produce edges for all components
        nodes = [i[0] for i in nx.connected_components(G)]
    else:
        # produce edges for components with source
        nodes = [source]
    # extra variables for cycle detection:
    cycle_stack = []
    output_cycles = set()

    def get_hashable_cycle(cycle):
        """cycle as a tuple in a deterministic order."""
        m = min(cycle)
        mi = cycle.index(m)
        mi_plus_1 = mi + 1 if mi < len(cycle) - 1 else 0
        if cycle[mi - 1] > cycle[mi_plus_1]:
            result = cycle[mi:] + cycle[:mi]
        else:
            result = list(reversed(cycle[:mi_plus_1])) + list(reversed(cycle[mi_plus_1:]))
        return tuple(result)

    for start in nodes:
        if start in cycle_stack:
            continue
        cycle_stack.append(start)

        stack = [(start, iter(G[start]))]
        while stack:
            parent, children = stack[-1]
            try:
                child = next(children)

                if child not in cycle_stack:
                    cycle_stack.append(child)
                    stack.append((child, iter(G[child])))
                else:
                    i = cycle_stack.index(child)
                    if i < len(cycle_stack) - 2:
                        output_cycles.add(get_hashable_cycle(cycle_stack[i:]))

            except StopIteration:
                stack.pop()
                cycle_stack.pop()

    return [list(i) for i in output_cycles]


analyzer = EmotionThesaurusBookAnalyzer()