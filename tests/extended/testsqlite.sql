

DROP TABLE IF EXISTS header;
CREATE TABLE `header` (
      `header_id` INTEGER NOT NULL PRIMARY KEY,
      `original_uid` INTEGER NOT NULL DEFAULT '0',
      `sent_date` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
      `epoch` INTEGER NOT NULL DEFAULT '0',
      `yard_phone` char(40) NOT NULL DEFAULT '',
      `tm` INTEGER NOT NULL DEFAULT '0',
      `id` INTEGER NOT NULL DEFAULT '0',
      `ref` INTEGER NOT NULL DEFAULT '0',
      `version` TEXT NOT NULL DEFAULT '',
      `recycler_id` INTEGER NOT NULL DEFAULT '0',
      `zip` TEXT DEFAULT NULL,
      `lat` decimal(20,15) DEFAULT NULL,
      `lng` decimal(20,15) DEFAULT NULL,
      `yard_alias` TEXT NOT NULL DEFAULT '',
      `yard_info` TEXT NOT NULL DEFAULT '',
      `yard_username` TEXT NOT NULL DEFAULT '',
      `yard_to` TEXT NOT NULL DEFAULT '""',
      `recycler_id_to` INTEGER NOT NULL DEFAULT '0',
      `to_zip` TEXT DEFAULT NULL,
      `to_lat` decimal(20,15) DEFAULT NULL,
      `to_lng` decimal(20,15) DEFAULT NULL,
      `to_username` TEXT NOT NULL DEFAULT '',
      `tag` text NOT NULL,
      `is_legacy` INTEGER NOT NULL DEFAULT '1',
      `is_response` INTEGER NOT NULL DEFAULT '0',
      `is_request` INTEGER NOT NULL DEFAULT '0',
      `batch_id` INTEGER NOT NULL DEFAULT '0',
      `insert_time` timestamp NOT NULL DEFAULT TEXT,
      `is_read` INTEGER NOT NULL DEFAULT '0'
)
;

DROP TABLE IF EXISTS request;
CREATE TABLE `request` (
  `request_id` INTEGER NOT NULL PRIMARY KEY,
  `header_id` INTEGER NOT NULL DEFAULT '0',
  `is_autoretail` INTEGER NOT NULL DEFAULT '0',
  `is_hl_request` INTEGER NOT NULL DEFAULT '0',
  `is_freeform` INTEGER NOT NULL DEFAULT '0',
  `is_image` INTEGER NOT NULL DEFAULT '0',
  `part_type` smallint(2) NOT NULL DEFAULT '0',
  `interchange` TEXT NOT NULL DEFAULT '',
  `rl_flag` char(1) NOT NULL DEFAULT '',
  `year` smallint(4) NOT NULL DEFAULT '0',
  `part_model_name` char(100) NOT NULL DEFAULT '',
  `description` text NOT NULL,
  `freeform_text` text NOT NULL,
  `batch_id` INTEGER NOT NULL DEFAULT '0',
  `insert_time` timestamp NOT NULL DEFAULT TEXT
)
;

DROP TABLE IF EXISTS htest;
CREATE TABLE htest (
    id INTEGER NOT NULL PRIMARY KEY,
    val TEXT
);

DROP TABLE IF EXISTS rtest;
CREATE TABLE rtest (
    rid INTEGER NOT NULL PRIMARY KEY,
    hid INTEGER NOT NULL DEFAULT '0',
    val2 TEXT,
    FOREIGN KEY(hid) REFERENCES htest(id)
);

INSERT INTO htest ( val ) VALUES ( 'TEST' );
INSERT INTO rtest ( hid, val2 ) VALUES ( 1, 'TEST2' );
