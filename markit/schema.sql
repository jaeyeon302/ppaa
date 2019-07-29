DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS mark;

CREATE TABLE user (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT NOT NULL UNIQUE,
	email TEXT UNIQUE NOT NULL CHECK(email like '%@%'),
	email_hash INTEGER UNIQUE NOT NULL,
	password TEXT NOT NULL,
	verified INTEGER NOT NULL DEFAULT 0,
	created TEXT NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE mark (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	user_id INTEGER NOT NULL,
	link TEXT NOT NULL,
	view_count INTEGER NOT NULL DEFAULT 0,
	created TEXT NOT NULL DEFAULT CURRENT_DATE,
	tag TEXT,
	FOREIGN KEY (user_id) REFERENCES user (id)
);