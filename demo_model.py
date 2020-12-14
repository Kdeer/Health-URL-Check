
import pickle
import numpy

# sudo 27 input parameters
sudo_test_parameters = [[-1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, 0,	1,	1,	1,	1,	-1, 1, -1, -1]]

# the function takes 27 input parameters to yield either -1 phishing or 1 legitimate
def svm_predict(parameters):
    filename = 'finalized_svm_mode.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    test_result = loaded_model.predict(parameters)
    print(test_result)
    return test_result[0]

svm_predict(sudo_test_parameters)


