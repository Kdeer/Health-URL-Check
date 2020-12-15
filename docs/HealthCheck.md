# Health-URL-Check

## 1. Frontend of EXtension

The extension code is currently written by `html+javascript+css`, the front-end flow chart of the execution is shown below:

```mermaid
graph TB
	subgraph Initializaion
		b1[Use Fethc to load the list of trusted domains in local json file] --> b2[Store the list of truseted domain in LocalStorage]
	end
	subgraph Plugin processing
        i1[Getting all <a> element] --> i2{Judge if URL is in the trusted domains list}
        i2 --url's domain is in trusted list--> i3(Ignorance)
        i2 --url's domain is not in trusted list--> i4[Extension tries to calculate the 17 features of all filtered URLs]
        i4 --Unable to get the html corresponding to the URL--> i5[Calculate 8 features related to the URL itself]
        i4 --Successfully get the html corresponding to the URL--> i6[Calculate 18 features related to the URL itself]
        i5 --> i7[Carry features to call a POST request to the backend to determine whether the URL is safe]
        i6 --> i7
        i7 --> i8{whether URL is safe or nor}
        i8 --URL is safe--> i9(Ignorance)
        i8 --URL is phishing--> i10[Extension processes the corresponding a tag to warn the user]
	end
```


## 2. Front-end communication format definition

> The communication format is json format

- Request format：

  ```json
  {
      "url": "https://www.baidu.com/img/1",
      "features": [
      	"feature1": 1,
          "feature2": 1,
          "feature3": 1,
          "feature4": 1,
          "feature5": 1,
          "feature6": 1,
          "feature7": 1,
          "feature10": 1,
          "feature11": 1,
          "feature12": 1,
          "feature13": 1,
          "feature14": 1,
          "feature15": 1,
          "feature16": 1,
          "feature20": 1,
          "feature21": 1,
          "feature23": 1,
      ]
  }
  ```

- Response format：

  ```json
  {
      "code": 0,						// 0 -> success -1 -> failed
      "msg": "",						// if failed, put error message here
      "data": {
          "security": true			// indicate if url is security
      }
  }
  ```

  
