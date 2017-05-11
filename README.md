Truckfinder
===========

Dev Environment Setup
---------------------
1 - Create a virtual environment

```bash
$ mkvirtualenv -p /usr/local/bin/python3.6 --no-site-packages truckfinder
```

2 - Create the local postgres user and database

```postgresql
CREATE USER truckfinder WITH PASSWORD 'truckfinder';
CREATE DATABASE truckfinder OWNER truckfinder;
```

3 - Install the required packages and `truckfinder` in edit mode

```bash
$ pip install -r requirements/local.txt
$ pip install -e .
```

Database Commands
-----------------
Autogenerate migrations

```bash
$ inv db_migrate
```

Apply all migrations

```bash
$ inv db_upgrade
```

Rollback to base

```bash
$ inv db_downgrade
```

Rollback to base and delete all migrations

```bash
$ inv db_purge
```

Build Commands
---------------
Build a new patch version:

```bash
```

Build a new minor version:
```bash
```

Build a new major version:
```bash
```
