
import pandas as pd
import numpy as np
from numpy import mean
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split, KFold, cross_val_score
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
from sklearn import svm
import pickle


'''
Data pre-processing 
correlations between each attributes will be check first. If |corr(A,B)| > 0.8, then they will be pruned

In the end, 27 attributes will be used, pruned attributes are 'Page_Rank', 'Links_pointing_to_page', 
'Domain_registration_length. Total 11055 entries will be used to train and test models.

The data is split by 70% train set, 30% test set. 
'''

dataset = pd.read_csv('phishing.csv')
# dataset.drop('index', axis=1, inplace=True)
# print(dataset.head())
# print(list(dataset.columns))

np.set_printoptions(precision=3, threshold=np.inf)
corr_dataset = np.corrcoef(dataset, rowvar=False)

feature_columns = list(dataset.columns)
feature_columns.pop()

for i in range(len(corr_dataset)):
    for j in range(i + 1, len(corr_dataset[i])):
        if corr_dataset[i][j] > 0.80 or corr_dataset[i][j] < -0.80:
            # print(i, ",", j)
            print(feature_columns[i], feature_columns[j])

# 27 parameters are used so far.
feature_columns.remove('Page_Rank')
feature_columns.remove('Links_pointing_to_page')
feature_columns.remove('Domain_registeration_length')


X = dataset[feature_columns]
y = dataset.Result
print(X.head())
ros = SMOTE(random_state=101, k_neighbors=5)
X_resample, y_resample = ros.fit_sample(X, y)

trainX, testX, trainY, testY = train_test_split(X_resample, y_resample, test_size=0.3, random_state=30)


'''
Two helper functions to determine the max and min number in a list with their indexes as well. 
They are used to help determine the best model parameters.
'''
def max_in_list(lst):
    the_max = 0
    index = 0
    for i in range(len(lst)):
        if lst[i] > the_max:
            the_max = lst[i]
            index = i

    return the_max, index

def min_diff(lst1, lst2):
    the_min = 1
    index = 0
    for i in range(len(lst1)):
        if lst1[i] - lst2[i] < the_min:
            index = i
            the_min = lst1[i] - lst2[i]
    return the_min, index


'''
svm_test() is used to select the best SVM model parameters
polynomial with degree or up has obvious edge than other kernel.

That is why a 10-Fold cross validation is performed on kernel = 'poly' with degrees iterates from 1 to 10. 
'''
def svm_test():
    degree = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    kernel = ['linear', 'poly', 'rbf', 'sigmoid']

    svmc = svm.SVC(gamma='scale', kernel='poly')
    # svmc.fit(trainX, trainY)

    #save the trained model
    # filename = 'finalized_svm_mode.sav'
    # pickle.dump(clf, open(filename, 'wb'))
    #
    # loaded_model = pickle.load(open(filename, 'rb'))
    # test_result = loaded_model.predict(testX)
    # print(loaded_model.score(testX, testY))
    cross_mean_list = []
    for i in range(1, 25):
        print("degree:", i)
        svmc.degree = i
        cv = KFold(n_splits=10, shuffle=True, random_state=1)
        cross_scores = cross_val_score(svmc, trainX, trainY, scoring="accuracy", cv=cv, n_jobs=-1)
        cross_mean_list.append(mean(cross_scores))

    max_mean, max_index = max_in_list(cross_mean_list)
    print("best degree is:", max_index+1)
    svmc.degree = max_index + 1
    svmc.fit(trainX, trainY)
    test_result = svmc.predict(testX)
    train_error = svmc.score(trainX, trainY)
    test_error = svmc.score(testX, testY)
    print("train error:", train_error, "test_error:", test_error)

    print("Prediction Result for kernel={}".format('poly'))
    print("confusion matrix")
    print(confusion_matrix(testY, test_result))
    tn, fp, fn, tp = confusion_matrix(testY, test_result).ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    print("Precision is: {:.4f}".format(precision))
    print("Recall is: {:.4f}".format(recall))
    f1_m = 2 * (precision * recall) / (precision + recall)
    print("F1 measurement is: {:.4f}".format(f1_m))
    print()

    plt.title('SVM Polynomials Cross Validation Score Mean')
    cross_line = plt.plot(cross_mean_list, '-r')
    plt.xlabel('Poly Degree')
    plt.ylabel('10-Fold Accuracy')
    plt.show()

# svm_test()
'''
'''

'''
backpropagation_test() is used to select the best backpropagation model parameters
solver = 'lbfgs' with activation function = 'logistic' are better than other solvers/activation function combination.

The max iteration from 700 to 1200 is iterated to determine the best iteration times based on the value of the
test set prediction. 

Result: 
lbgfs solver, logistics activation, 900 iterations
0.9825 / 0.9667
Confusion Matrix
[1798    62]
[61    1774]
Precision 0.9662
Recall 0.9668
F1 Measurement 0.9665
'''
def backpropagation_test():
    iter = [700, 750, 800, 850, 900, 950, 1000, 1050, 1100, 1150, 1200]
    solvers = ['lbfgs', 'sgd', 'adam']
    activations = ['identity', 'logistic', 'tanh', 'relu']
    hidden_layer = len(feature_columns)
    # print(hidden_layer)
    train_score_list = []
    test_score_list = []
    bpc = MLPClassifier(solver="lbfgs", activation="logistic",
                        hidden_layer_sizes=(hidden_layer*2, hidden_layer*4, ))
    for i in iter:
        print("prediction result on {} iterations, lbfgs solver, logistic activation".format(i))
        bpc.max_iter = i
        bpc.fit(trainX, trainY)
        train_accuracy = bpc.score(trainX, trainY)
        test_accuracy = bpc.score(testX, testY)
        train_score_list.append(train_accuracy)
        test_score_list.append(test_accuracy)
        print("train error:", train_accuracy, "test_error:", test_accuracy)

    plt.title('Backp train accuracy and test accuracy')
    plt.plot(train_score_list, '-r', label="Train Acc")
    plt.plot(test_score_list, '-g', label="Test Acc")
    plt.xlabel("Iteration Index, 0 = 700, 10 = 1200")
    plt.ylabel("Accuracy")
    plt.legend()
    plt.show()

    the_min, index = min_diff(train_score_list, test_score_list)

    print("min different between train and test set:", the_min, "index of the iteration:", index)
    bpc.max_iter = iter[index]
    bpc.fit(trainX, trainY)
    test_result = bpc.predict(testX)
    train_accuracy = bpc.score(trainX, trainY)
    test_accuracy = bpc.score(testX, testY)
    print("train error:", train_accuracy, "test_error:", test_accuracy)

    print(confusion_matrix(testY, test_result))
    tn, fp, fn, tp = confusion_matrix(testY, test_result).ravel()
    precision = tp/(tp+fp)
    recall = tp/(tp+fn)
    print("Precision: {:.4f}".format(precision))
    print("Recall: {:.4f}".format(recall))
    f1_m = 2*(precision*recall)/(precision+recall)
    print("F1 measurement: {:.4f}".format(f1_m))
    print()

# backpropagation_test()



'''
random_forest_test() is used to select the best random_forest_test model parameters
gini index is better than entropy criterion. 
a 10-Fold cross validation is performed on n_estimators = 10 to 300. 

Result:
gini, cross validation best n_estimators = 50, mean = 0.964
train error: 0.9824805661909735 test_error: 0.96914749661705 
[[1798   62] 
[  52 1783]]
Precision is: 0.9664
Recall is: 0.9717
F1 measurement is: 0.9690  
'''
def random_forest_test():
    cross_mean_list = []
    rfc = RandomForestClassifier(n_estimators=10, criterion='gini', random_state=50, warm_start=True)
    test_error_list = []

    for i in range(1, 30):
        print(i)
        cv = KFold(n_splits=10, shuffle=True, random_state=1)
        cross_scores = cross_val_score(rfc, trainX, trainY, scoring="accuracy", cv=cv, n_jobs=-1)
        cross_mean_list.append(mean(cross_scores))
        rfc.n_estimators += 10
    #
    # max_mean, max_index = max_in_list(cross_mean_list)
    # max_mean_test, max_index_test = max_in_list(test_error_list)
    # print("cross validate max and index:", max_mean, max_index)
    rfc.n_estimators = (4+1)*10
    rfc.fit(trainX, trainY)
    test_result = rfc.predict(testX)
    train_error = rfc.score(trainX, trainY)
    test_error = rfc.score(testX, testY)
    print("train error:", train_error, "test_error:", test_error)
    test_result = rfc.predict(testX)
    print(confusion_matrix(testY, test_result))
    tn, fp, fn, tp = confusion_matrix(testY, test_result).ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    print("Precision is: {:.4f}".format(precision))
    print("Recall is: {:.4f}".format(recall))
    f1_m = 2 * (precision * recall) / (precision + recall)
    print("F1 measurement is: {:.4f}".format(f1_m))
    print()

    filename = 'finalized_rf_mode.sav'
    pickle.dump(rfc, open(filename, 'wb'))
    loaded_model = pickle.load(open(filename, 'rb'))
    train_error = loaded_model.score(trainX, trainY)
    test_error = loaded_model.score(testX, testY)

    print("train error:", train_error, "test_error:", test_error)
    test_result = loaded_model.predict(testX)
    print(confusion_matrix(testY, test_result))
    tn, fp, fn, tp = confusion_matrix(testY, test_result).ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    print("Precision is: {:.4f}".format(precision))
    print("Recall is: {:.4f}".format(recall))
    f1_m = 2 * (precision * recall) / (precision + recall)
    print("F1 measurement is: {:.4f}".format(f1_m))
    print()

    plt.title('Random Forest Gini Cross Validation Score Mean')
    cross_line = plt.plot(cross_mean_list, '-r')
    plt.xlabel("n_enum: 0=10, 30=300")
    plt.ylabel("accuracy in Mean")
    plt.show()


    # plt.plot(validate_error_list, '-g')
    # plt.show()


# random_forest_test()


'''
Save the finalized svm model to finalized_svm_mode.sav
final saved model has gamma='scale' with kernel = 'poly', degree = 9
Then load it to test the result
'''
def finalize_svm():
    svmc = svm.SVC(gamma='scale', kernel='poly', degree=9)
    svmc.fit(trainX, trainY)
    filename = 'finalized_svm_mode.sav'
    pickle.dump(svmc, open(filename, 'wb'))

    loaded_model = pickle.load(open(filename, 'rb'))
    test_result = loaded_model.predict(testX)
    print(loaded_model.score(testX, testY))

    test_result = loaded_model.predict(testX)
    print(confusion_matrix(testY, test_result))
    tn, fp, fn, tp = confusion_matrix(testY, test_result).ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    print("Precision is: {:.4f}".format(precision))
    print("Recall is: {:.4f}".format(recall))
    f1_m = 2 * (precision * recall) / (precision + recall)
    print("F1 measurement is: {:.4f}".format(f1_m))
    print()


# finalize_svm()
'''
Save the finalized backpropagation model to finalized_backp_mode.sav
final saved model has solver='lbfgs' with criterion = 'logistic', hidden layer 1 = 54, hidden layer 2 = 108
max_iter = 900
Then load it to test the result
'''
def finalize_backpropagation():

    hidden_layer = len(feature_columns)
    bpc = MLPClassifier(solver="lbfgs", activation="logistic",
                        hidden_layer_sizes=(hidden_layer*2, hidden_layer*4, ), max_iter=900)
    bpc.fit(trainX, trainY)
    filename = 'finalized_backp_mode.sav'
    pickle.dump(bpc, open(filename, 'wb'))

    loaded_model = pickle.load(open(filename, 'rb'))
    test_result = loaded_model.predict(testX)
    print(loaded_model.score(testX, testY))

    test_result = loaded_model.predict(testX)
    print(confusion_matrix(testY, test_result))
    tn, fp, fn, tp = confusion_matrix(testY, test_result).ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    print("Precision is: {:.4f}".format(precision))
    print("Recall is: {:.4f}".format(recall))
    f1_m = 2 * (precision * recall) / (precision + recall)
    print("F1 measurement is: {:.4f}".format(f1_m))
    print()

# finalize_backpropagation()


'''
Save the finalized random forest model to finalized_rf_mode.sav
final saved model has n_estimators = 50 with criterion = "gini"
Then load it to test the result
'''

def finalize_random_forest():
    rfc = RandomForestClassifier(n_estimators=50, criterion='gini', random_state=50)
    rfc.fit(trainX, trainY)
    filename = 'finalized_rf_mode.sav'
    pickle.dump(rfc, open(filename, 'wb'))
    loaded_model = pickle.load(open(filename, 'rb'))

    test_result = loaded_model.predict(testX)
    print(confusion_matrix(testY, test_result))
    tn, fp, fn, tp = confusion_matrix(testY, test_result).ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    print("Precision is: {:.4f}".format(precision))
    print("Recall is: {:.4f}".format(recall))
    f1_m = 2 * (precision * recall) / (precision + recall)
    print("F1 measurement is: {:.4f}".format(f1_m))
    print()


# finalize_random_forest()


'''
Final voting function test.
'''
def voting_test():
    file_backp = 'finalized_backp_mode.sav'
    file_rf = 'finalized_rf_mode.sav'
    file_svm = 'finalized_svm_mode.sav'
    load_backp = pickle.load(open(file_backp, 'rb'))
    load_rf = pickle.load(open(file_rf, 'rb'))
    load_svm = pickle.load(open(file_svm, 'rb'))

    backp_test_result = load_backp.predict(testX)
    svm_test_result = load_svm.predict(testX)
    rf_test_result = load_rf.predict(testX)

    voting_list = []
    for i in range(len(backp_test_result)):
        if backp_test_result[i] == svm_test_result[i] or backp_test_result[i] == rf_test_result[i]:
            voting_list.append(backp_test_result[i])
        else:
            voting_list.append(svm_test_result[i])

    print(confusion_matrix(testY, voting_list))
    tn, fp, fn, tp = confusion_matrix(testY, voting_list).ravel()
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    print("Precision is: {:.4f}".format(precision))
    print("Recall is: {:.4f}".format(recall))
    f1_m = 2 * (precision * recall) / (precision + recall)
    print("F1 measurement is: {:.4f}".format(f1_m))
    print()


# voting_test()

