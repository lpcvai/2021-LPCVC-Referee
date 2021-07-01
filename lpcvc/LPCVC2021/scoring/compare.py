from .data_set import DataSet


def calculate_correct(correct, submitted):
    num_correct = 0
    num_attributes = 0
    for k, v in correct.items():
        if k != 'frame':
            num_attributes += 1
            if k in submitted and v == submitted[k]:
                num_correct += 1
    return (0, 0) if num_attributes == 0 else (num_correct, num_attributes - num_correct)


class Compare:

    def __init__(self, correct: DataSet, submitted: DataSet, threshold):
        self.correct = correct
        self.submitted = submitted
        self.threshold = threshold
        self.same_points = DataSet()
        self.prRcList = []
        self.numAttributes = correct.get_itemLength()
        self.totalAttributes = correct.items_len * self.numAttributes
        self.currCorrect = 0
        self.currIncorrect = 0
        self.compare()

    def compare(self):
        self.correct.items_pos = 0
        for i in self.submitted:
            item = self.correct.get_item_from_threshold(i['frame'], self.threshold, remember_pos=True)
            self.same_points.add_item(item)

    def num_correct(self):
        num_correct = 0
        for c, s in zip(self.same_points, self.submitted):
            if None not in [c, s]:
                correct, incorrect = calculate_correct(c, s)
                self.currCorrect += correct
                self.currIncorrect += incorrect
            else:
                self.currIncorrect += self.numAttributes

            self.prRcList.append([(self.currCorrect / (self.currCorrect + self.currIncorrect)),
                                  (self.currCorrect / self.totalAttributes)])
        return num_correct

    def interPolateAP(self):
        i = len(self.prRcList) - 1
        maxPrecision = self.prRcList[i][0]
        while i >= 0:
            maxPrecision = max(self.prRcList[i][0], maxPrecision)
            self.prRcList[i][0] = maxPrecision
            i -= 1

    def fixprRcList(self):
        newPrRcList = []
        if len(self.prRcList) <= 1:
            return
        minVal = self.prRcList[0][0]

        for i in self.prRcList:
            if len(newPrRcList) == 0:
                newPrRcList.append(i)
            elif i[1] == newPrRcList[len(newPrRcList) - 1][1]:
                newPrRcList[len(newPrRcList) - 1][0] = min(newPrRcList[len(newPrRcList) - 1][0], i[0])
            else:
                newPrRcList.append(i)
        self.prRcList = newPrRcList

    def calcmAP(self):
        score = 0
        if len(self.prRcList) <= 1:
            return 0

        # added minor bug fix
        # self.prRcList.insert(0, [self.prRcList[0][0], 0.0])
        i = len(self.prRcList) - 1
        curPrecision = self.prRcList[i][0]
        curRecall = self.prRcList[i][1]

        while i >= 0:
            if self.prRcList[i][0] != curPrecision:
                score += curPrecision * (curRecall - self.prRcList[i][1])
                curRecall = self.prRcList[i][1]
                curPrecision = self.prRcList[i][0]
            i -= 1
        score += curPrecision * curRecall
        return score

    def description_score(self):
        num_correct = self.num_correct()
        self.fixprRcList()
        self.interPolateAP()
        score = self.calcmAP()

        return {
            'precision & recall': self.prRcList,
            'score': score,
            'total_score': num_correct,
            'total_frames': len(self.same_points),
            'missing_num_frame': len(self.correct) - len(self.same_points),
        }

    @property
    def score(self):
        score = self.description_score()
        return score['precision & recall']

    def __str__(self):
        return 'Score: {}\n'.format(str(self.score))
