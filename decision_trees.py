import csv
import math
import random
import operator
from sklearn import tree
import copy

dic = {}
col = []
original_test_set = []

def decision_trees(training_file, test_file):
    
    
    print("decision trees start point")
    result = []
    try:
        clf = tree.DecisionTreeClassifier()
        
        #initialize training set(including header and species)
        training_set = read_csv(training_file, True) 
        #print(training_set[1:])
        training_data_set = []
        training_target_set = []

        #format data and target training set
        for x in range(len(training_set)):
            if x == 0: continue #header
            training_data_set.append(training_set[x][:-1])
            training_target_set.append(training_set[x][-1])
       
        #print(training_data_set)
        #print(training_target_set)
        
        #generate the model
        clf.fit(training_data_set, training_target_set)
        
        #initialize testing set(including header)
        test_set = read_csv(test_file, False)
        #print(test_set)
        
        result = clf.predict(test_set[1:])
        #print(result)
        
        number_of_attributes = len(test_set[0])
        for x in range (len(test_set)):
            if x == 0:
                test_set[x].append(training_set[0][number_of_attributes])
                original_test_set[x].append(training_set[0][number_of_attributes])
                continue #header
            test_set[x].append(result[x-1])
            original_test_set[x].append(result[x-1])
        str_result = ""
        for row in original_test_set:
                str_result = str_result + ", ".join(str(e).strip() for e in row) + "\n"        
        print (str_result)
        return str_result
        
    except Exception as e:
        print (e)
        print ("Error in main decision_trees function")    
        exit(-1)
        
   
    
    
def read_csv(filename, is_training):
    print("decision trees start reading csv")
    dataset = []
    global dic
    global col
    global original_test_set    
    try:
        with open(filename, newline='') as csvfile:
            lines = csv.reader(csvfile, delimiter=',')
            for line in lines:
                if len(line) > 0:
                    dataset.append(line)
            #dataset = list(lines) #list of list
            #print(dataset)
            number_of_columns = len(dataset[0])
            if is_training:
                check_column = number_of_columns - 1
            else:
                check_column = number_of_columns
                original_test_set = copy.deepcopy(dataset)
            
            col = [1000] * check_column
            
            for x in range(len(dataset)):
                if x == 0: continue #header

                for y in range(check_column):
                    try:
                        dataset[x][y] = float(dataset[x][y])
                    except:
                        if y in dic:
                            dic_inner = dic[y]
                            if str(dataset[x][y]) in dic_inner:
                                dataset[x][y] = float(dic_inner[dataset[x][y]])
                            else:
                                col[y] = col[y] + 1
                                dic_inner[dataset[x][y]] = col[y]
                                dataset[x][y] = float(col[y])
                                
                        else:
                            dic[y] = {str(dataset[x][y]):col[y]}
                            dataset[x][y] = float(col[y])                        
                        
                    
        return dataset
    except Exception as e:
        print(e)
        exit(-1)
                
        
    
#decision_trees("C:\\Users\\xinjaguo\\Desktop\\dataset\\iris\\iris_training.csv", "C:\\Users\\xinjaguo\\Desktop\\dataset\\iris\\iris_test.csv")
#decision_trees("C:\\Users\\xinjaguo\\Desktop\\dataset\\adult\\adult_training.csv", "C:\\Users\\xinjaguo\\Desktop\\dataset\\adult\\adult_test.csv")
#decision_trees("C:\\Users\\xinjaguo\\Desktop\\dataset\\poker\\poker_training.csv", "C:\\Users\\xinjaguo\\Desktop\\dataset\\poker\\poker_test.csv")