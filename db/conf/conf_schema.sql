-- SQLite

DROP TABLE IF EXISTS timeslots;
DROP TABLE IF EXISTS overview;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS presentations;

PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS timeslots
(
  Id INTEGER PRIMARY KEY,
  Date DATE,
  Start_time TIME,
  End_time TIME
);

CREATE TABLE IF NOT EXISTS overview
(
  Id INTEGER PRIMARY KEY,
  Date DATE,
  Start_time TIME,
  End_time TIME,
  Type VARCHAR,
  timeslot_id INT NOT NULL,
  FOREIGN KEY
(timeslot_id) REFERENCES timeslots
(Id)

);

CREATE TABLE IF NOT EXISTS sessions
(
  Id INTEGER PRIMARY KEY,
  type VARCHAR,
  roomnumber VARCHAR,
  timeslot_id INT NOT NULL,
  presentation_id INT NOT NULL,
  img VARCHAR,
  FOREIGN KEY (timeslot_id) REFERENCES timeslots(Id),
  FOREIGN KEY (presentation_id) REFERENCES presentations(Id)
);


CREATE TABLE IF NOT EXISTS presentations
(
  Id INTEGER PRIMARY KEY,
  title VARCHAR,
  authors VARCHAR,
  presenter_name VARCHAR,
  presenter_email VARCHAR,
  mode VARCHAR,
  keywords VARCHAR,
  presenter_bio TEXT,
  picture VARCHAR
);