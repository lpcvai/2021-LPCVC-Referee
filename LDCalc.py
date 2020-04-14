# install with pip3 install python-Levenshtein
from Levenshtein import distance
from collections import OrderedDict
import itertools
import sys


# Method to read a text file: "txtName"
def reader(txtName):
    with open(txtName) as txt:
        dict = OrderedDict()
        # Reading all lines in A.txt into keysAndVals
        keysAndValsOG = txt.readlines()
        keysAndValsOG = [x.lower() for x in keysAndValsOG]
        i = 0
        key = []  # Seperate array to store keys
        val = []  # Seperate array to store values

        ii = 0
        semiPos = 0
        keysAndVals = keysAndValsOG

        # Converting one line default answer format to newlines
        for value in keysAndValsOG[0]:
            if keysAndValsOG[0][ii] == ';':
                semiPos = ii
            elif keysAndValsOG[0][ii] == ':':
                if (semiPos != 0):
                    keysAndVals[0] = keysAndValsOG[0][0:semiPos] + '|' + keysAndValsOG[0][(semiPos+1):]
            ii += 1
        keysAndVals = keysAndValsOG[0].split("|")

        # Creating dictionary for reader
        for value in keysAndVals:
            keyVal1st = keysAndVals[i].split(":")
            val1st = keyVal1st[1].split(";")
            keyVal = []
            keyVal.append(keyVal1st[0])
            j = 0
            for value in val1st:
                keyVal.append(val1st[j])
                j += 1
            j = 0
            key.append(keyVal[0].rsplit())
            innerValList = []
            j = 0
            for value in keyVal:
                if(j != 0):
                    innerValList.append(keyVal[j].rsplit())
                j += 1
            val.append(innerValList)
            i += 1
        i = 0
        i = 0
        # TODO Remove test prints when done
        # print(key)
        # print(val)
        # For every value in key update dictionary with next key and value
        for value in key:
            keyNow = str(key[i])
            dict.update({keyNow: val[i]})
            i += 1
        # TODO Remove test print loop when done
        '''
        print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
        for keys,values in dict.items():
            print(keys)
            print(dict[keys])
        '''
    return dict

def flatten(data):
    merged = list(itertools.chain(*data))
    return merged

# Method to calculate the distance between the values between two dictionaries
def distanceCalc(realATxtName, aTxtName):
    # Initializing variables and calling reader
    realADict = reader(realATxtName)
    aDict = reader(aTxtName)
    for key in aDict.keys():
        if aDict[key] == [[]]:
            aDict[key] = [[""]]
    distList = []
    totAns = 0
    avgDistDouble = None

    # Creating combinations of different answers for each key
    frameAnsCombList = []
    #print(realADict)
    for key in realADict:
        allRealAnswers = flatten(realADict[key])
        allAnswers = flatten(aDict[key])
        for realAnswer in allRealAnswers:
            currFrame = []
            if allAnswers == []:
                currFrame.append([realAnswer, ""])
                frameAnsCombList.append(currFrame)
                continue
            for answer in allAnswers:
                currFrame.append([realAnswer, answer])
            frameAnsCombList.append(currFrame)

    # Evaluating distance across frameAnsCombList into frameAnsScoreList
    frameAnsScoreList = []
    for i in range(len(frameAnsCombList)):
        groundTruth = frameAnsCombList[i][0][0]
        minScore = float("inf")
        for dataValue in frameAnsCombList[i]:
            lvDist = distance(groundTruth, dataValue[1])
            if lvDist < minScore:
                minScore = lvDist
        # frameAnsScoreList format : ["groundTruth", minScore]
        frameAnsScoreList.append([groundTruth, minScore])

    finalScore = finalScoreCalculator(frameAnsScoreList)
    return finalScore


# Calculates final score from a score list
def finalScoreCalculator(scoreList):
    finalScore = 0.0
    for item in scoreList:
        wordLength = len(item[0])
        currScore = item[1]
        # Basing score on ratio between LD Score and word length
        currFinal = float(currScore / wordLength)
        if currFinal > 1:
            currFinal = 1
        finalScore += currFinal
    return float(finalScore / len(scoreList))


if __name__ == '__main__':
     if len(sys.argv) == 3:
         avgDist = distanceCalc(sys.argv[1], sys.argv[2])
         print("%f" %(1 - avgDist))
     else:
         print("Incorrect number of arguments. Found {:d}, expected 3".format(len(sys.argv)))
