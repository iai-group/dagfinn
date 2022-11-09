# Actions

Below you can information related to the different actions with indications on what should be changed to fit your use case.

## Conference sessions

Before starting the actions server, the following global variables should be replaced in this [file](action_conf_sessions.py) to match your use case:

* ENDDATE: End date of the conference
* DB_NAME: Conference database name 

There are 3 functions that should be updated.

* [check_day](action_conf_sessions.py#L568): update the mapping between week days and dates
* [ActionKeynoteInfo.run](action_conf_sessions.py#L387): update the day associated to each keynote
* [ActionConferenceSchedule.run](action_conf_sessions.py#L461): update how the schedule picture retrieval (e.g., from local files, from database)

## Recommend POI

Before starting the actions server, the following global variables should be replaced in this [file](action_recommend_poi.py) to match your use case:
* DB_NAME: POI database name
* CONFERENCE_ADDRESS: Address of the conference venue 
* MAPS: City where the conference is taking place 
