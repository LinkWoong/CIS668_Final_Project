# CIS668_Final_Project
Sentimental analysis for YouTube comments

# Project Proposal (DDL Nov.1st)
[Project proposal](https://www.overleaf.com/project/5f78874f228fa60001a8f4f0)
- [ ] Find suitable pretrained NLP model that could be applied directly without training (Bert?)
- [ ] Youtube public [APIs](https://developers.google.com/youtube/v3/docs/search/list) GET/POST (Multi-thread, data pre-processing, limitation etc.)
- [ ] Weekly milestones completed by group members (Also assign tasks to each of group member)
- [ ] Sync thru Zoom every week

# Weekly milestones (starting from Nov.1st)

## Youtube public data APIs (Week 11, Nov.2nd to Nov.8th)
- [ ] Implement download comments from specific Youtube videos
- [ ] Preprocessing and data cleaning (nulls check, emoji etc.)
- [ ] Normalize the comments

Google official Python API client repository:
> [https://github.com/googleapis/google-api-python-client](https://github.com/googleapis/google-api-python-client)

YouTube Python API:
> [https://github.com/youtube/api-samples/tree/master/python](https://github.com/youtube/api-samples/tree/master/python)

## Bert Model Training and fine-tuning (Week 12-13, Nov.9th - Nov.24th)
- [ ] Feed the data into the model, compare the output with groundtruth
- [ ] Fine-tune parameters (Are we doing binary classification here? i.e. 1 for positive emotion and -1 for negative?)
- [ ] Results explanation and investigation

This part is going to be implemented by: 

## Project report composition and slides (Along with previous milestones)
- [ ] Write the complete report
- [ ] Design slides

This part is going to be implemented by: 
