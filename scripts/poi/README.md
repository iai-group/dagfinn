# POI

This folder contains scripts to create a POI database from [Tripadvisor](https://www.tripadvisor.com).

## Create POI database

1. Collect the top attractions and restaurants from Tripadvisor with the following command:
```bash
python -m scripts.poi.tripadvisor_poi_collection \
 --attraction-link https://www.tripadvisor.com/Attractions-g190511-Activities-Stavanger_Stavanger_Municipality_Rogaland_Western_Norway.html \
 --restaurant-link https://www.tripadvisor.com/Restaurants-g190511-Stavanger_Stavanger_Municipality_Rogaland_Western_Norway.html \
 --output-file db/poi/data/poi.tsv
```
2. Insert previously collected POIs into the database with the following command:
```bash
$ sqlite3 db/poi.db < db/poi/poi_schema.sql
$ python -m scripts.poi.populate_poi_db \
 --data-file db/poi/data/poi.tsv \
 --db-name poi
```
