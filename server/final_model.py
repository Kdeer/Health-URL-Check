import pickle
import numpy

'''
pseudo 27 input parameters, orders are
1. having_IPhaving_IP_Address, 
2. URLURL_Length, 
3. Shortining_Service, 
4. having_At_Symbol,
5. double_slash_redirecting, 
6. Prefix_Suffix, 
7. having_Sub_Domain, 
8. SSLfinal_State, 
9. Favicon, 
10. port,	
11. HTTPS_token, 
12. Request_URL, 
13. URL_of_Anchor, 
14. Links_in_tags, 
15. SFH, 
16. Submitting_to_email, 
17. Abnormal_URL, 
18. Redirect, 
19. on_mouseover, 
20. RightClick, 
21. popUpWidnow, 
22. Iframe, 
23. age_of_domain, 
24. DNSRecord, 
25. web_traffic, 
26 Google_Index, 
27. Statistical_report
'''
sudo_test_parameters = [[-1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, 0, 1, 1, 1, 1, -1, 1, -1, -1]]


# the function takes 27 input parameters to yield either -1 phishing or 1 legitimate

# voting system


def finalized_backp_predict(parameters):
    filename = 'finalized_backp_mode.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    test_result = loaded_model.predict(parameters)
    print("backp result:", test_result[0])
    return test_result[0]


def finalized_svm_predict(parameters):
    filename = 'finalized_svm_mode.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    test_result = loaded_model.predict(parameters)
    print("svm result:", test_result[0])
    return test_result[0]


# random forest is finalized
def finalize_random_forest(parameters):
    filename = 'finalized_rf_mode.sav'
    loaded_model = pickle.load(open(filename, 'rb'))

    test_result = loaded_model.predict(parameters)
    print("RF result:", test_result[0])
    return test_result[0]


def get_voting_result(parameters):
    backp_test_result = finalized_backp_predict(parameters)
    svm_test_result = finalized_svm_predict(parameters)
    rf_test_result = finalize_random_forest(parameters)

    if backp_test_result == svm_test_result or backp_test_result == rf_test_result:
        print("Voting Result:", backp_test_result)
        return backp_test_result
    else:
        print("Voting Result:", svm_test_result)
        return svm_test_result


# result = get_voting_result(sudo_test_parameters)
# print("voting result:", result)
