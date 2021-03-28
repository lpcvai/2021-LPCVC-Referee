from .data_set import DataSet


def calculate_correct(expected, actual):
    num_correct = 0
    num_attributes = 0
    for k, v in expected.items():
        if k != 'frame':
            num_attributes += 1
            if k in actual and v == actual[k]:
                num_correct += 1
    return 0 if num_attributes == 0 else num_correct / num_attributes


class Compare:

    def __init__(self, correct: DataSet, submitted: DataSet, threshold):
        self.expected = correct
        self.actual = submitted
        self.threshold = threshold
        self.same_points = DataSet()
        self.compare()

    def compare(self):
        self.expected.items_pos = 0
        for i in self.actual:
            item = self.expected.get_item_from_threshold(i['frame'], self.threshold, remember_pos=True)
            self.same_points.add_item(item)

    def correct(self):
        num_correct = 0
        for e, a in zip(self.actual, self.same_points):
            if None not in [e, a]:
                num_correct += calculate_correct(e, a)
        return num_correct

    def description_score(self):
        num_correct = self.correct()
        return {
            'total_score': num_correct,
            'total_frames': len(self.same_points),
            'missing_num_frame': len(self.expected) - len(self.same_points),
        }

    @property
    def score(self):
        score = self.description_score()
        total_frames = score['total_frames']
        return score['total_score'] / total_frames if total_frames > 0 else 0

    def __str__(self):
        return 'Score: {:.2}\n'.format(self.score)
