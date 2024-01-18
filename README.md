## Deployment
### Start Flask backend
- In the project directory:
```
python3 -m venv myenv
sudo apt-get install libpq-dev python3-dev
source myenv/bin/activate
pip install -r requirements.txt
python3 server.py
```

### Start React frontend
- https://learn.microsoft.com/en-us/windows/dev-environment/javascript/nodejs-on-wsl
- In the project directory:
```
source ~/.bashrc
npx create-react-app someaitools
npm install
npm start
```

### Start PostgreSQL database
```
sudo -i -u postgres
psql -U postgres -d postgres
ALTER ROLE maxloo CREATEDB;
\du

psql -U maxloo -d postgres
CREATE DATABASE someaitools
\connect someaitools
psql -U maxloo -d someaitools
sudo -i -u postgres
psql
GRANT ALL PRIVILEGES ON DATABASE someaitools TO maxloo;
ALTER USER maxloo WITH PASSWORD '4444';

\i ./db/init_db.sql
sudo service postgresql restart
sudo service postgresql status

DELETE FROM users;
COMMIT;
SELECT * FROM users;
```

### Start MariaDB database
- https://kontext.tech/article/1031/install-mariadb-server-on-wsl
- https://mariadb.com/resources/blog/using-sqlalchemy-with-mariadb-connector-python-part-1/
- https://mariadb.com/docs/server/connect/programming-languages/c/install/
- https://stackoverflow.com/questions/51603067/installing-connector-c-for-mariadb
- https://cloud.mariadb.com/csm?id=my_customer_token

sudo /etc/init.d/mariadb start
sudo /etc/init.d/mariadb status
sudo mysql_secure_installation
sudo mariadb
CREATE USER 'maxloo'@'localhost' IDENTIFIED BY '4444';
GRANT ALL PRIVILEGES ON *.* TO 'maxloo'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
SELECT user, host, plugin FROM mysql.user;

mariadb -u maxloo -p
CREATE DATABASE someaitools;
USE someaitools;
SOURCE /home/maxloo/src/someaitools/pdf/db/init_db.sql;
SHOW DATABASES
SHOW TABLES;
DESCRIBE users;