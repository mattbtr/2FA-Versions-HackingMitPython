# Db-Zugriffe regelna etc.

# Überprüfen ob mysql_native_password plugin aktiviert ist:
#SELECT plugin_name, plugin_status 
#FROM information_schema.plugins 
#WHERE plugin_name LIKE 'validate%';
-- > nicht genutzt


# set password policy -- nicht gemacht
#SET GLOBAL validate_password_policy=LOW;

# create users
#CREATE USER "ticketdb_user"@"%" IDENTIFIED WITH mysql_native_password BY "Heute0000"
CREATE USER "ticketdb_user"@"%" IDENTIFIED BY "Heute0000"

-- Schritt 1: Datenbankspezifische Privilegien vergeben
GRANT CREATE, ALTER, DROP, INSERT, UPDATE, DELETE, SELECT, REFERENCES  
ON ticketdb.*  
TO 'ticketdb_user'@'%'  
WITH GRANT OPTION;  

-- Schritt 2: Globales RELOAD-Privileg zum Neuladen der Serverkonfiguration 
GRANT RELOAD  
ON *.*  
TO 'ticketdb_user'@'%';  

# Privilegien anzeigen:
SHOW GRANTS FOR "ticketdb_user"@"%";

# Alle Privilegien entfernen eines Users ggf.:
-- REVOKE ALL ON *.* ON "ticketdb_user"@"%";
