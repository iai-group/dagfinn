-- SQLite
DROP TABLE IF EXISTS busRoute;
DROP TABLE IF EXISTS POI;
DROP TABLE IF EXISTS POITag;

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS busRoute (
    rid INTEGER PRIMARY KEY AUTOINCREMENT,
    origin TEXT,
    destination TEXT,
    busNum TEXT,
    duration INTEGER
);

CREATE TABLE IF NOT EXISTS POI (
    pid INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    rating REAL,
    price INTEGER,
    address TEXT,
    busStop TEXT,
    distanceFromBusStop INTEGER,
    website TEXT,
    googleMapsID TEXT
);

CREATE TABLE IF NOT EXISTS POITag (
    pid INTEGER,
    tag TEXT NOT NULL,
    PRIMARY KEY (pid, tag),
    FOREIGN KEY (pid) REFERENCES POI(pid)
);
    