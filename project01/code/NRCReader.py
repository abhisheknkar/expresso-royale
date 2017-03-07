import time

def NRCReader(filepath='../../data/common-data/lexicons/NRC_Emotion.txt'):
    f = open(filepath,'r')
    nrcDict = {}
    for line in f.readlines():
        lsplit = line.strip().split()
        if lsplit[0] not in nrcDict:
            nrcDict[lsplit[0]] = []
        if lsplit[2] == '1':
            nrcDict[lsplit[0]].append(lsplit[1])
    f.close()
    return nrcDict

if __name__ == '__main__':
    t0 = time.time()
    nrcDict = NRCReader()
    print 'Time taken: ', time.time()-t0