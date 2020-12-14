import pickle
import numpy

'''
pseudo 27 input parameters, orders are
1. having_IPhaving_IP_Address,   => function 1 （1.1.1）
2. URLURL_Length,                => function 2 （1.1.2）
3. Shortining_Service,           => function 3 （1.1.3）
4. having_At_Symbol,             => function 4 （1.1.4）
5. double_slash_redirecting,     => function 5 （1.1.5）
6. Prefix_Suffix,                => function 6 （1.1.6）
7. having_Sub_Domain,            => function 7 （1.1.7）
8. SSLfinal_State,               => function 8 （1.1.8）
9. Favicon,                      => function 10 （1.1.10）
10. port,	                     => function 11 （1.1.11）
11. HTTPS_token,                 => function 12 （1.1.12）
12. Request_URL,                 => function 13 （1.2.1）
13. URL_of_Anchor,               => function 14 （1.2.2）
14. Links_in_tags,               => function 15 （1.2.3）
15. SFH,                         => function 16（1.2.4）
16. Submitting_to_email,         => function 17（1.2.5）
17. Abnormal_URL,                => function 18 （1.2.6）
18. Redirect,                    => function 19 （1.3.1）
19. on_mouseover,                => function 20 （1.3.2）
20. RightClick,                  => function 21 （1.3.3）
21. popUpWidnow,                 => function 22 （1.3.4）
22. Iframe,                      => function 23 （1.3.5）
23. age_of_domain,               => function 24 （1.4.1）
24. DNSRecord,                   => function 25 （1.4.2）
25. web_traffic,                 => function 26 （1.4.3）
26 Google_Index,                 => function 28 （1.4.5）
27. Statistical_report           => function 30 （1.4.7）
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


