# install with pip3 install python-Levenshtein
from Levenshtein import distance
from collections import OrderedDict


# Class for Answer Reader
class answerReader:
    # Method to read a text file: "txtName"
    def reader(txtName):
        with open(txtName) as txt:
            dict = OrderedDict()
            # Reading all lines in A.txt into keysAndVals
            keysAndValsOG = txt.readlines()
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


class levenshteinD:
    # Method to calculate the distance between the values between two dictionaries
    def distanceCalc(realATxtName, aTxtName):
        # Initializing variables and calling reader
        realADict = answerReader.reader(realATxtName)
        aDict = answerReader.reader(aTxtName)
        distList = []
        totAns = 0
        avgDistDouble = None

        # Creating combinations of different answers for each key
        frameAnsCombList = []
        for key in realADict:
            frameAnsCombinations = [[real, gen] for real in realADict[key] for gen in aDict[key]]
            #print(frameAnsCombinations)
            frameAnsCombList.append(frameAnsCombinations)
        keyInd = 0
        for key in frameAnsCombList:
            ansMacMatchInd = 0
            for ansMacMatch in frameAnsCombList[keyInd]:
                frameAnsCombList[keyInd][ansMacMatchInd] = [[real, gen] for real in \
                    frameAnsCombList[keyInd][ansMacMatchInd][0] for gen in \
                        frameAnsCombList[keyInd][ansMacMatchInd][1]]
                ansMacMatchInd += 1
            keyInd += 1
        '''
        print("-----------------------")
        print(frameAnsCombList[0][0][0])
        '''
        # Creating list of distances between each possible combination of answers to each key
        distList = frameAnsCombList
        keyInd = 0
        for key in frameAnsCombList:
            ansMacMatchInd = 0
            for ansMacMatch in frameAnsCombList[keyInd]:
                ansInnMatchInd = 0
                for ansInnMatch in frameAnsCombList[keyInd][ansMacMatchInd]:
                    '''
                    print("--------------------------------")
                    print(keyInd)
                    print(ansMacMatchInd)
                    print(ansInnMatchInd)
                    print(distance(distList[keyInd][ansMacMatchInd][ansInnMatchInd][0], \
                        distList[keyInd][ansMacMatchInd][ansInnMatchInd][1]))
                    print(distList)
                    '''
                    distList[keyInd][ansMacMatchInd][ansInnMatchInd] = distance \
                        (distList[keyInd][ansMacMatchInd][ansInnMatchInd][0], \
                            distList[keyInd][ansMacMatchInd][ansInnMatchInd][1])
                    ansInnMatchInd += 1
                ansMacMatchInd += 1
            keyInd += 1

        # Flattening distList (There is unecessary nested lists right now)
        keyInd = 0
        for key in distList:
            flatRealADictStr = []
            for sublist in distList[keyInd]:
                for val in sublist:
                    flatRealADictStr.append(val)
            distList[keyInd] = flatRealADictStr
            keyInd += 1
        #print("---------------------------------------------------")
        #print(distList)

        # Applying selection sort (least to greatest) to distList
        keyInd = 0
        minI = 0
        for key in distList:
            for i in range(len(distList[keyInd])):
                # Find the minimum element in remaining
                minI = i
                for j in range(i+1, len(distList[keyInd])):
                    if distList[keyInd][minI] > distList[keyInd][j]:
                        minI = j
                # Swap the found minimum element with minI       
                distList[keyInd][i], distList[keyInd][minI] = distList[keyInd][minI],\
                    distList[keyInd][i] 
            keyInd += 1
        #print(distList)

        # Creating a related array to distList with the number of words per key in realADict
        totalWord = []
        for key in realADict:
            totalWordInKey = []
            '''
            for val in realADict:
                print(key)
                print(realADict[key])
                totalWordInKey.append(len(realADict[key]))
            totalWord.append(sum(totalWordInKey))
            '''
            totalWord.append(len(realADict[key]))
        #print(totalWord)

        # Calculating total Levenshtein Distance per key in distListSumOfKey list 
        distListSumOfKey = []
        keyInd = 0
        for key in distList:
            #print(distList[keyInd][0:totalWord[keyInd]])
            distListSumOfKey.append(sum(distList[keyInd][0:totalWord[keyInd]]))
            keyInd += 1
        #print(distListSumOfKey)
        #print(frameAnsCombList[0][0])
        #print([[real, gen] for real in frameAnsCombList[0][0][0] for gen in frameAnsCombList[0][0][1]])

        # Calculating and Returning average distance
        if (len(distListSumOfKey) != 0):
            avgDistDouble = sum(distListSumOfKey)/len(distListSumOfKey)
        
        return avgDistDouble

#print("Import levenshteinD and answerReader classes instead and run levenshteinD.distanceCalc()")
avgDist = levenshteinD.distanceCalc("realA.txt", "A.txt")
print("The error of the solution is: %f" %(avgDist))