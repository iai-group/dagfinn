# Conference data

This folder is reserved for scripts related to the creation of a database with conference information. 
As each conference has a different website, we cannot provide scripts to scrape conference data and populate the database.

The schema of the conference database is available [here](../../db/conf/conf_schema.sql).

We recommend to gather the following information regarding the accepted contributions and schedule to get a working solution:
* Contributions
    * Session name
    * Title
    * Authors
    * Picture
    * Bio
    * Keywords
* Schedule
    * Time slot
    * Date
    * Name of the session
    * Link to a picture of the session schedule

## Toy example

The folder contains a script to create a database for a toy example.
Follow the instructions below to create the associated database.

```bash
$ sqlite3 db/conference.db < db/conf/conf_schema.sql
$ python -m scripts.conf.add_conference_data \
 --timetable-file db/conf/data/toy_example_timetable.csv \
 --contributions-file db/conf/data/toy_example_contributions.csv \
 --db-name conference
```

Note: if you want to use local images for the session schedule, you need to place them in the folder `ui/furhat-screen/assets/conf_images` and add the path in the database.