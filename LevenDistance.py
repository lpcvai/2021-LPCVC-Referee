import csv

def LD(s, t): #https://www.python-course.eu/levenshtein_distance.php

	if len(s) == 0:
		return len(t)
	if len(t) == 0:
		return len(s)
	if s == "":
		return len(t)
	if t == "":
		return len(s)
	if s[-1] == t[-1]:
		cost = 0
	else:
		cost = 1

	res = min([LD(s[:-1], t)+1,
               LD(s, t[:-1])+1, 
               LD(s[:-1], t[:-1]) + cost])

	return res




def main():
	answersCSV = []
	submissionCSV = []
	#read and store answers
	with open('sample_answers.csv', mode='r') as csvfile:
		readCSV = csv.reader(csvfile, delimiter=',')
		answersCSV = next(readCSV)



	#read submission and compare and output to csv file
	with open('sample_grading.csv', mode='w') as output_file:
		output = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		headerRow = answersCSV
		headerRow.insert(0, "Team Name");
		output.writerow(headerRow)
		with open('sample_submission.csv', mode='r') as submission:
			readCSV = csv.reader(submission, delimiter=',')
			for row in readCSV:
				sub = row
				sub[0].replace('\ufeff', '')
				#compare
				if sub[0] != '\ufeffTeam Name':
					result = []
					for i in range(1, len(sub), 1):
						result.append(LD(answersCSV[i-1], sub[i]))
					result.insert(0, sub[0])
					output.writerow(result)







if __name__ == "__main__":
	main()