# install with pip3 install python-Levenshtein
import re
from Levenshtein import distance
from collections import OrderedDict


# Class for Answer Reader
class answerReader:
    # Method to read a text file: "txtName"
    def reader(txtName):
        with open(txtName) as txt:
            aDict = OrderedDict()
            # Reading all lines in A.txt into keysAndVals
            keysAndVals = txt.readlines()
            i = 0
            key = []  # Seperate array to store keys
            val = []  # Seperate array to store values
            ''' outline in meeting 2/9
            for val(txt.readline()):
                if a(val) == ';':
                    semiPos = val
                else if a(val) == ':':
                    a(semiPos) = '\n'
            '''


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
                aDict.update({keyNow: val[i]})
                i += 1
            # TODO Remove test print loop when done

            print("-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=")
            for keys,values in aDict.items():
                print(keys)
                print(aDict[keys])
            
        #return aDict


class levenshteinD:
    # Method to calculate the distance between val in dict
    def distanceCalc():
        # Initializing variables and calling reader
        realADict = answerReader.reader("realA.txt")
        aDict = answerReader.reader("A.txt")
        distList = []
        avgDistDouble = None
        # Iterating and calculating distance for each key in realADict
        for key in realADict:
            # Flattening realADict values for this key into one list
            flatRealADictStr = []
            for sublist in realADict[key]:
                for val in sublist:
                    flatRealADictStr.append(val)
            realADict[key] = flatRealADictStr
            # print(" ".join(realADict[key]))
            # Flattening aDict values for this key into one list
            flatADictStr = []
            for sublist in aDict[key]:
                for val in sublist:
                    flatADictStr.append(val)
            aDict[key] = flatADictStr
            # print(" ".join(aDict[key]))
            # Appending the distance between
            distList.append(distance(" ".join(" ".join(realADict[key])),
                                     " ".join(" ".join(aDict[key]))))
        # Calculating and Returning average distance
        if (len(distList) != 0):
            avgDistDouble = sum(distList)/len(distList)
        return avgDistDouble


avgDist = levenshteinD.distanceCalc()
print(avgDist)
