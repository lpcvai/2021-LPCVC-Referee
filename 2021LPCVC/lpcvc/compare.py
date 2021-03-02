from lpcvc import DataSet


def calculate_correct(expected, actual):
    num_correct = 0
    num_attributes = 0
    for k, v in expected.items():
        if k != 'Frame':
            num_attributes += 1
            if v == actual[k]:
                num_correct += 1
    return 0 if num_attributes == 0 else num_correct / num_attributes


class Compare:

    def __init__(self, expected: DataSet, actual: DataSet, threshold):
        self.expected: DataSet = expected
        self.actual: DataSet = actual
        self.threshold = threshold
        self.same_points: DataSet = DataSet()
        self.compare()

    def compare(self):
        self.expected.items_pos = 0
        for i in self.actual:
            item = self.expected.get_item_from_threshold(i['Frame'], self.threshold, remember_pos=True)
            self.same_points.add_item(item)

    def correct(self):
        num_correct = 0
        for e, a in zip(self.actual, self.same_points):
            if None not in [e, a]:
                num_correct += calculate_correct(e, a)
        return num_correct

    def score(self):
        num_correct = self.correct()
        num_incorrect = len(self.same_points) - num_correct
        return {
            'correct_num_frame': num_correct,
            'incorrect_num_frame': num_incorrect,
            'missing_num_frame': len(self.expected) - len(self.same_points),
            'excess_num_frame': self.same_points.num_excess()
        }
