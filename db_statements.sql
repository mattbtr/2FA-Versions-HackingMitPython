# Löshen der Tabellen
DROP TABLE IF EXISTS bugusers;
DROP TABLE IF EXISTS bugitems;

# Tabellen erstellen
CREATE TABLE bugitems(
	id INT NOT NULL AUTO_INCREMENT,
	priority INT NOT NULL,
	username VARCHAR(30) NOT NULL,
	title VARCHAR(64) NOT NULL,
	description VARCHAR(512) NOT NULL,
	PRIMARY KEY(id)
);

CREATE TABLE bugusers(
	id INT NOT NULL AUTO_INCREMENT,
	username VARCHAR(30) NOT NULL unique,
	email_address VARCHAR(50) NOT NULL unique,
	password VARCHAR(30) NOT NULL,
	PRIMARY KEY(id)
);

#ALTER TABLE bugusers ADD UNIQUE(username);
#ALTER TABLE bugusers ADD UNIQUE(email_address);

# Tabellen von ausgewählter DB anzeigen
SHOW TABLES;

# Anzeigen der Eigenschaften von Tabellenspalten
DESCRIBE bugitems;
DESCRIBE bugusers;

# insert intos
INSERT INTO bugitems(id, priority, username, title, DESCRIPTION) VALUES(1 ,2, "Luke", "GUI-Problem", "Gui not working");
INSERT INTO bugitems VALUES (2, 2, "Natalie", "Backend problem", "Backend NOT STARTING");
INSERT INTO bugitems VALUES (3, 3, "Anakin", "Totally broken", "Nothing works");

INSERT INTO bugusers(id, username, email_address, PASSWORD) VALUES(1, "Derk", "derk@web.de", "pass");
INSERT INTO bugusers VALUES(2, "Natalie", "natalie@web.de", "pass");
INSERT INTO bugusers VALUES(3, "Anakin", "anakin@web.de", "pass");

SELECT * FROM bugitems;
SELECT * FROM bugusers;