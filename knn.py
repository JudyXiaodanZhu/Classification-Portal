import csv
import math
import random
import operator
import boto3
import copy

dic = {}
col = []
original_test_set = []

def knn(training_file_name, test_file_name):
    print("knn start running")
    result = ''
    global original_test_set
    try:
        s3 = boto3.resource('s3', region_name='us-east-1')
        bucket_name = "judydataset"
		
        #initialize training set(including header and species)
        training_obj = s3.Object(bucket_name, training_file_name)
        training_file_lines = training_obj.get()['Body'].read().decode('utf8')
        training_set = read_csv_lines(training_file_lines, True) 
        #print(training_set)
        
        #initialize testing set(including header)
        test_obj = s3.Object(bucket_name, test_file_name)
        test_file_lines = test_obj.get()['Body'].read().decode('utf8')
        test_set = read_csv_lines(test_file_lines, False)
        #print(test_set)
        
        number_of_attributes = len(test_set[0])
        for x in range(len(test_set)):
            if x == 0:
                test_set[x].append(training_set[0][number_of_attributes])
                original_test_set[x].append(training_set[0][number_of_attributes])
                continue #header
            nearest_neighbor = get_nearest_neighbor(training_set, test_set[x], number_of_attributes)
            species = nearest_neighbor[number_of_attributes]
            test_set[x].append(species)
            original_test_set[x].append(species)
        #print ("result: " + str(result))
        for row in original_test_set:
            result = result + ", ".join(str(e).strip() for e in row) + "\n"
        print(result)
        return result     
        
    except Exception as e:
        print ("Error in main knn function")
        print(e)
    
def calculate_distance(training_instance, test_instance, number_of_attributes):
    #print("calculate distance")
    distance = 0.0
    for x in range(number_of_attributes):
        distance = distance + pow(float(training_instance[x]) - float(test_instance[x]), 2)
    return math.sqrt(distance)

def get_nearest_neighbor(training_set, test_instance, number_of_attributes):
    try:
       #print("find nearest neighbor")
        nearest_neighbor_index = None
        nearest_neighbor_distance = float('inf')
        
        for x in range(len(training_set)):
            if x == 0: continue #header
            distance = calculate_distance(training_set[x], test_instance, number_of_attributes)
            if distance < nearest_neighbor_distance:
                nearest_neighbor_distance = distance
                nearest_neighbor_index = x
        return training_set[nearest_neighbor_index]
    except Exception as e:
        print(e)
        return -1
    
#def read_csv(filename, is_training):
def read_csv_lines(lines, is_training):
    print("knn start reading csv")
    dataset = []
    global dic
    global col
    global original_test_set
    try:
        #with open(filename, newline='') as csvfile:
            #lines = csv.reader(csvfile, delimiter=',')
        for row in lines.split("\n"):
            if len(str(row).strip()) > 0:
                dataset.append((row.split(',')))
			
        #print(dataset)
        number_of_columns = len(dataset[0])
        if is_training:
            check_column = number_of_columns - 1
        else:
            check_column = number_of_columns
            original_test_set = copy.deepcopy(dataset)
            #print(original_test_set)
            
        
        col = [1000] * check_column
        
        for x in range(len(dataset)):
            if x == 0: continue      
            
            for y in range(check_column):
                try:
                    dataset[x][y] = float(dataset[x][y])
                except:
                    #thorws exception
                    #print("Error : files:" + filename + " contains non numerical values on line #" + str(x+1) + ",column #" + str(y+1))
                    #exit(-1)
                    #convert format
                
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
            
        print(dic)           
        return dataset
    except Exception as e:
        print(e)
        #print(dataset)
        exit(-1)

