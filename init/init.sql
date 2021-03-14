\c db_iptocountry

CREATE TABLE IF NOT EXISTS T_IP_TO_COUNTRY (
	id INTEGER NOT NULL,
	ip_from BIGINT NOT NULL,
	ip_from_str varchar(15) NOT NULL, 
	ip_to BIGINT NOT NULL,
	ip_to_str varchar(15) NOT NULL,
	registry varchar(20) NOT NULL,
	assigned INTEGER NOT NULL,
	ctry varchar(2) NOT NULL,
	cntry varchar(3) NOT NULL,
	country varchar(100) NOT NULL, 
	CONSTRAINT T_IP_COUNTRY_PK PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS T_CONFIG (
	key_id varchar(100) NOT NULL,
	param_value varchar(100) NOT NULL, 
	CONSTRAINT T_CONFIG_PK PRIMARY KEY (key_id)
);

INSERT INTO T_CONFIG (key_id, param_value) VALUES ('LATEST_FILE_EPOCH', '0');
