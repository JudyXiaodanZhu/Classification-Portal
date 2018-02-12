from flask import Flask, redirect, render_template, url_for, flash, request
import requests
import boto3
import os
import decision_trees

ALLOWED_EXTENSIONS = set(['csv'])

render_result = False
# initializes app and connect to db
app = Flask(__name__)

@app.route('/')
# Returns the dashboard page which displays all 4 managerUI functionality
def index():
    return render_template('dashboard.html')


#Helper function
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():

    #check Training and Test Data
    if 'training_file' not in request.files:
      return render_template('dashboard.html', upload_err = "Missing upload training file!")
    
    if 'test_file' not in request.files:
      return render_template('dashboard.html', upload_err = "Missing upload test file!")
      
    training_file = request.files['training_file']
    test_file = request.files['test_file']
    
    if training_file.filename == '':
      return render_template('dashboard.html', upload_err = "Missing Training Data!")
      
    if test_file.filename == '':
      return render_template('dashboard.html', upload_err = "Missing Test Data!")
    
    if allowed_file(training_file.filename) == False:
      return render_template('dashboard.html', upload_err = "Training Data type: only .csv is allowd!")
      
    if allowed_file(test_file.filename) == False:
      return render_template('dashboard.html', upload_err = "Test Data type: only .csv is allowd!")
    
    #if (training_file.filename == test_file.filename):
      #return render_template('dashboard.html', upload_err = "Training and Test file Names can not be the same!")
     
    
    #everything is pass we need to upload them to s3 'judydataset bucket'
    fname_training = os.path.join('/tmp/', training_file.filename)
    fname_test = os.path.join('/tmp/', test_file.filename)
    
    training_file.save(fname_training)
    test_file.save(fname_test)
    
    #check contents of Training and Test Data
    f_train = open(fname_training,"r")
    header_train = f_train.readline().split(",")
    f_test = open(fname_test,"r")
    header_test = f_test.readline().split(",")
    
    if(len(header_train) != len(header_test) + 1):
      return render_template('dashboard.html', upload_err = "The format of either Training Data or Test Data is not correct, please see the 'Template'!")
    
    for i in range (len(header_test)):
      if header_train[i].strip() != header_test[i].strip():
         return render_template('dashboard.html', upload_err = "The format of either Training Data or Test Data is not correct, please see the 'Template'!")
    
    #now 
    s3 = boto3.resource('s3')
    f_train = open(fname_training, "rb")
    s3.Bucket("judydataset").put_object(Key=training_file.filename, Body=f_train, ACL='public-read')
    f_test = open(fname_test, "rb")
    s3.Bucket("judydataset").put_object(Key=test_file.filename, Body=f_test, ACL='public-read')
     
    algorithm = request.form['algo']
    #knn
    if algorithm.strip() == 'knn': 
      #call knn lambda funtion
      training_file_name = training_file.filename
      test_file_name = test_file.filename
      url = "https://o135tona4i.execute-api.us-east-1.amazonaws.com/prod?training=%s&test=%s" % (training_file_name, test_file_name)
      r = requests.get(url).json()
    #decision tree
    else:
      r = decision_trees.decision_trees(fname_training, fname_test)
    #set up values
    rows = r.split("\n")
    header = rows[0].split(",")
    data = rows[1:]
    #store solution file into s3
    output_file_name = "/tmp/result_%s.csv" % (algorithm.strip())
    f_w = open(output_file_name, "w")
    f_w.write(r)
    f_w.close()
    f_r = open(output_file_name, "rb")
    s3.Bucket("judydataset").put_object(Key="result_%s.csv" % (algorithm.strip()), Body=f_r, ACL='public-read')
    f_r.close()
    #render page
    global render_download
    render_result = True
    download_url = "https://s3.amazonaws.com/judydataset/result_%s.csv" % (algorithm.strip()) 
    return render_template('dashboard.html', header = header, data = data, download_url = download_url, render_result = render_result)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)



