CREATE TABLE word (
  ID INTEGER PRIMARY KEY AUTOINCREMENT,
  lemma TEXT,
  pos TEXT,
  flag INTEGER
);

CREATE TABLE parse (
  ID INTEGER PRIMARY KEY AUTOINCREMENT,
  raw TEXT,
  wid INTEGER NOT NULL,
  preds INTEGER,
  FOREIGN KEY (wid) REFERENCES word(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "flag" (
    "ID" INTEGER PRIMARY KEY NOT NULL,
    "text" TEXT,
    "desc" TEXT
);

CREATE INDEX word_lemma ON word(lemma);
CREATE INDEX word_flag ON word(flag);

INSERT INTO "flag" (ID, text, desc)
VALUES
    (1, 'PROCESSED', ''),
    (2, 'ERROR', 'couldn''t parse'),
    (3, 'GOLD', ''),
    (4, 'COMPOUND', 'to be further processed, but most likely are compound'),
    (5, 'MWE', 'compound that were confirmed are multi-word expressions'),
    (6, 'MISMATCHED', 'wrong POS'),
    (7, 'UNKNOWN', ''),
    (8, 'NOM_VERB', 'norminalized'),
    (9, 'COMP_NN', 'Noun-noun compound'),
    (10, 'COMP_AN', 'Adj-noun compound'),
    (11, 'COMP_NE', 'named-entity');
