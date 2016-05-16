# -*- coding: utf-8 -*-
import os
from reader import Proposer
import pandas as pd


def readpath(path, output, outputtype):
    userfiles = pd.Series()
    for file in os.listdir(path):
        user = file.split("_")[0]
        if user not in userfiles.keys():
            userfiles[user] = []
        userfiles[user].append(file)
        userfiles.sort_values(inplace=True)
    avg_recall = []
    avg_precision = []
    with open(output, outputtype) as f:
        for user in userfiles.keys():
            if len(userfiles[user]) == 0:
                continue
            # Make an array with all the click actions of one user
            allrows = []
            for file in userfiles[user]:
                try:
                    iterrows = iter(open(path + "/"+file))
                    for row in iterrows:
                        if row.split(',')[1].replace("\"", "").strip() == "click":
                            row = clean_file_row(row)
                            # If an empty row (eg end of file) or JS link
                            if not row and "javascript" not in row.lower():
                                continue
                            allrows.append(row)
                except:  # If an import still fails, skip & keep count
                    print("Skipped file ", file)
            # Cut 80% of the data
            datacut = round(len(allrows)/100*80)
            proposer = Proposer(path, False)
            for row in allrows[:datacut]:
                try:
                    proposer.parse_action(row)
                except:
                    print(file)
            # Use the last 20% of data to score the results based on the given
            # predictions towards the actual next website
            recall = 0.0  # relevant retrieved / relevant
            precision = 0.0  # relevant retrieved / retrieved
            totalscore = 0
            endlist = 4
            for rowindex in range(0, len(allrows[datacut:])-4):
                proposals = proposer.parse_action(allrows[rowindex], False, 5)
                if proposals is not None:
                    for i in range(0, len(proposals)):
                        if proposals[i] in [allrows[rowindex+1].split(',')[3],
                                     allrows[rowindex+2].split(',')[3],
                                     allrows[rowindex+3].split(',')[3]]:
                            recall += 1 
                            precision += 1.0/(i+1)
                            totalscore += (len(proposals) - i)
                            break
            totalscore /= (len(allrows) - datacut-3)
            recall /= (len(allrows) - datacut-3)
            precision /= (len(allrows) - datacut-3)
            avg_recall.append(recall)
            avg_precision.append(precision)
            f.write(user + " " + str(totalscore) + " " + 
                    str(recall) + " " + str(precision) + " " + 
                    str(len(allrows[datacut:])-1) + "\n" )
    print(avg_recall)
    print("AVG recall:", (sum(avg_recall) / len(avg_recall)))
    print(avg_precision)
    print("AVG precision:", (sum(avg_precision) / len(avg_precision)))


def clean_file_row(input):
    """ Cleans the input string from double quotes, \n and whitespaces """
    input = input.rstrip()
    input = "".join(input.split())
    input = input.replace("\"", "")
    return input


def test_together():  
    """ This function will loop through all files and test the
    correctness of the proposer """
    readpath('./data', './results/alldata.txt', 'w+')


def test_seperately():
    """ This function will loop through the different users and test the
    correctness of the proposer """
    users = []
    for i in [x for x in range(1,28) if not x == 9 or not x == 10]:
        users.append("u"+str(i))
    for user in users:
        readpath('./testdata/'+user, './results/seperate.txt', 'a')


#test_together()  # Tests all files together
test_seperately()  # Test seperately per user
