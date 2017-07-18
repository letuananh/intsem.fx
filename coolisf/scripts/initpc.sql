/* Init parse cache DB */
CREATE TABLE sent (
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       text TEXT NOT NULL,
       pc INTEGER,
       tagger TEXT,
       grm TEXT NOT NULL,
       xml TEXT
);

CREATE TABLE parse (
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       sid INTEGER REFERENCES sent(ID) ON UPDATE CASCADE,
       pid TEXT,
       ident TEXT,
       jmrs TEXT,
       jdmrs TEXT,
       mrs TEXT,
       dmrs TEXT
);

CREATE INDEX sent_text ON sent(text);
CREATE INDEX sent_grm ON sent(grm);
CREATE INDEX parse_ID ON parse(ID);
CREATE INDEX parse_sid ON parse(sid);
CREATE INDEX parse_pid ON parse(pid);
CREATE INDEX parse_ident ON parse(ident);
