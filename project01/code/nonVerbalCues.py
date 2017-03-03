class EmotionThesaurusBookAnalyzer():
    def __init__(self, path):
        self.book = open(path, "rb")

    def getContent(self,pStart,pEnd=-1):
        if pEnd == -1:
            pEnd = pStart + 1
        content = ''
        for i in range(pStart,pEnd):
            x = self.pdf.getPage(i).extractText()+'\n'
            content += x
            print x
        # content = " ".join(content.replace(u"\xa0", " ").strip().split())
        return content

analyzer = EmotionThesaurusBookAnalyzer('/home/abhishek/Desktop/EmotionThesaurus.pdf')
analyzer.getContent(22)