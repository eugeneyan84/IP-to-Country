# IP-to-Country Tool

## Overview
A simple CLI tool that attempts to map a provided IPv4 address to its origin country. Latest IP to country data is derived from Webnet77 archive [here](http://software77.net/geo-ip/history/). The tool also provides a means to look up the top-ranking countries in terms of their cumulative quantities of uniquely assigned IP addresses.

The tool is backed by a Postgres database encapsulated within a Docker container to hold the IP to country records. A dockerized pgAdmin web-portal has also been included for convenient access to the database.

Access credentials for pgAdmin web-portal (http://localhost:80) are enclosed in the `docker-compose.yml` file.  Postgres database credentials are enclosed in the `config.json` file.

## Pre-requisites

In order to run this tool, the following must already be installed:
- Docker and Docker-Compose (Instructions can be found [here](https://www.techiediaries.com/ubuntu/install-docker-19-docker-compose-ubuntu-20-04/))
- Python 3.x
- Virtualenv (Instructions can be found [here](https://pypi.org/project/virtualenv/))

Ensure Docker service is running.

## Folder Structure
| File               | Description                                                                                                                                                       |
|--------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| init/init.sql      | SQL script for setting up tables in Postgres database. This script is referenced by `docker-compose.yml`.                                                         |
| config.json        | Holds configuration values, such as URL for ip-to-country data file and database credentials.                                                                     |
| db_util.py         | Provides methods for retrieving and updating Postgres db records. Also holds the query for aggregating the top-ranking countries in terms of cumulative IP range. |
| docker-compose.yml | Configuration file for building the database and pgAdmin Docker images.                                                                                           |
| ip_util.py         | Provides methods to validate IPv4 address string, as well as conversion functionality for IP address octet representation <-> numeric representation.             |
| LICENSE            | GNU General Public License v3.0.                                                                                                                                  |
| main.py            | Entry point for IP-to-Country tool.                                                                                                                               |
| README.md          | Current file.                                                                                                                                                     |
| requirements.txt   | Manifest of necessary packages to run this tool. Used in `pip` command for installation.                                                                          |
| web_util.py        | Provides methods for web scraping the target website for the direct-download link of the latest data file, as well as data extraction from CSV file.              |

## Database Table Definitions

### t_ip_to_country
| Column      | Type   | Description                                                                                                                                                                                                                   |
|-------------|--------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| id          | int    | Record identifier                                                                                                                                                                                                             |
| ip_from     | bigint | Lower boundary IPv4 address in numeric format of a given IP range in a record  <br/>Example: (from Right to Left) 1.2.3.4 = 4 + (3 * 256) + (2 * 256 * 256) + (1 * 256 * 256 * 256) <br/>is 4 + 768 + 13,1072 + 16,777,216 = 16,909,060 |
| ip_from_str | string | Lower boundary IPv4 address in octet string format of a given IP range in a record                                                                                                                                            |
| ip_to       | bigint | Upper boundary IPv4 address in numeric format of a given IP range in a record                                                                                                                                                 |
| ip_to_str   | string | Upper boundary IPv4 address in octet string format of a given IP range in a record                                                                                                                                            |
| registry    | string | apnic, arin, lacnic, ripencc and afrinic                                                                                                                                                                                      |
| assigned    | int    | The date this IP or block was assigned. (In Epoch seconds)                                                                                                                                                                    |
| ctry        | string | 2 character international country code                                                                                                                                                                                        |
| cntry       | string | 3 character international country code                                                                                                                                                                                        |
| country     | string | Full Country Name                                                                                                                                                                                                             |

### t_config
| Column      | Type   | Description                                                  |
|-------------|--------|--------------------------------------------------------------|
| key_id      | string | Holds configuration key.                                     |
| param_value | string | Holds the value associated with the given configuration key. |

## Installation & Usage
1. Clone this repository.
```bash
$ git clone https://github.com/eugeneyan84/IP-to-Country.git
```
2. Navigate to the IP-to-Country folder:
```bash
$ cd IP-to-Country
```
3.  There is a `docker-compose.yml` file in the IP-to-Country folder that would provide the relevant configuration specifications to run a Postgres database (exposed on port 5432), alongside a pgAdmin web-interface (exposed on port 80). Build the images and start up the containers in daemon-mode:
```bash
$ sudo docker-compose up -d
```
4. Verify that the Docker containers `pg_admin` and `pg_db` are running:
```bash
$ sudo docker container ps

CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                         NAMES
3b668ccece2e        dpage/pgadmin4      "/entrypoint.sh"         1 minute ago        Up 1 minute         0.0.0.0:80->80/tcp, 443/tcp   pg_admin
86f4996728a6        postgres            "docker-entrypoint.s…"   1 minute ago        Up 1 minute         0.0.0.0:5432->5432/tcp        pg_db
```
5. In the same IP-to-Country directory, create new virtual environment called `env`:
```bash
$ python3 -m venv env
```
6. Activate the newly created virtual environment with the `source` command:
```bash
$ source env/bin/activate
(env) $
```
7. Install the necessary packages that have been defined in the `requirements.txt` file by running the following `pip` command:
```bash
(env) $ pip install -r requirements.txt
```
8. At this point, setup of all necessary packages and respective Docker database service have been completed.  The entry-point of the tool is `main.py`. Take note that first-run of this tool would be slow, as it attempts to populate the database with data extracted from the web-source. You can view a IP to country mapping (e.g. 43.60.163.91) with the following command:
```bash
(env) $ python3 main.py -map 43.60.163.91

Search result for 43.60.163.91:
[
    {
        "country": "Singapore",
        "ip_range": "43.0.0.0 - 43.127.255.255"
    }
]
```
9. Top-ranking countries (e.g. top 3) can be viewed with the following command:
 ```bash
(env) $ python3 main.py -top 3

[
    {
        "country": "United States",
        "total_num_unique_ips": 1615203936,
        "ip_range_size_rank": 1
    },
    {
        "country": "China",
        "total_num_unique_ips": 344411648,
        "ip_range_size_rank": 2
    },
    {
        "country": "Japan",
        "total_num_unique_ips": 190071296,
        "ip_range_size_rank": 3
    }
]
```
> Written with [StackEdit](https://stackedit.io/).
