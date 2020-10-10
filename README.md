# CIS668_Final_Project
Sentimental analysis for YouTube comments

# Project Proposal (DDL Nov.1st)
[Project proposal](https://www.overleaf.com/project/5f78874f228fa60001a8f4f0)
- [ ] Find suitable pretrained NLP model that could be applied directly without training (Bert?)
- [x] Youtube comment download feature ([APIs](https://developers.google.com/youtube/v3/docs/search/list))
- [ ] Model training and fine-tuning

# Weekly milestones (starting from Nov.1st)

## Youtube public data APIs (Week 11, Nov.2nd to Nov.8th)
- [x] Implement download comments from specific Youtube videos
- [ ] Preprocessing and data cleaning (nulls check, emoji etc.)

I've finished developing download comments from Youtube. Please see [downloader.py](https://github.com/LinkWoong/CIS668_Final_Project/blob/main/downloader.py) for details. Below is the working principle of this youtube comment downloader.py.
![Architecture](https://github.com/LinkWoong/CIS668_Final_Project/blob/main/img/architecture.png)

### Installation
TL;DR: just simply install **requirements.txt**
```pip install requirements.txt```

Prerequisites:
- Python Version >= 3.7
- pip
- The Google APIs Client Library for Python:  
```pip install --upgrade google-api-python-client```
- The google-auth, google-auth-oauthlib, and google-auth-httplib2 for user authorization  
```pip install --upgrade google-auth google-auth-oauthlib google-auth-httplib2```
- Requests  
```pip install requests```
- lxml  
```pip install lxml```
- cssselect  
```pip install cssselect```


Resources:
Google official Python API client repository:
> [https://github.com/googleapis/google-api-python-client](https://github.com/googleapis/google-api-python-client)

YouTube Python API:
> [https://github.com/youtube/api-samples/tree/master/python](https://github.com/youtube/api-samples/tree/master/python)


## Bert Model Training and fine-tuning (Week 12-13, Nov.9th - Nov.24th)
- [ ] Feed the data into the model, compare the output with groundtruth
- [ ] Fine-tune parameters (Are we doing binary classification here? i.e. 1 for positive emotion and -1 for negative?)
- [ ] Results explanation and investigation

## Project report composition and slides (Along with previous milestones)
- [ ] Write the complete report
- [ ] Design slides
