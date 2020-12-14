import pickle
import numpy

'''
pseudo 27 input parameters, orders are
1. having_IPhaving_IP_Address,   => function 1 （1.1.1）
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
sudo_test_parameters = [[-1, 1, 1, 1, -1, -1, -1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, 0,	1,	1,	1,	1,	-1, 1, -1, -1]]

# the function takes 27 input parameters to yield either -1 phishing or 1 legitimate
def svm_predict(parameters):
    filename = 'finalized_svm_mode.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    test_result = loaded_model.predict(parameters)
    print(test_result)
    return test_result[0]

svm_predict(sudo_test_parameters)


