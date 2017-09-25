/* Init ACE cache DB */
CREATE TABLE sent (
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       text TEXT NOT NULL,
       grm TEXT NOT NULL,
       pc INTEGER,
       extra_args TEXT
);

CREATE TABLE mrs (
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       sid INTEGER REFERENCES sent(ID) ON UPDATE CASCADE,
       mrs TEXT
);

CREATE INDEX sent_text ON sent(text);
CREATE INDEX sent_grm ON sent(grm);
CREATE INDEX sent_pc ON sent(pc);
CREATE INDEX sent_extra_args ON sent(extra_args);
CREATE INDEX mrs_sid ON mrs(sid);
