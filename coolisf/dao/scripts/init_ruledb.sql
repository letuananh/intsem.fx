CREATE TABLE lexunit (
  ID INTEGER PRIMARY KEY AUTOINCREMENT,
  lemma TEXT,
  pos TEXT,
  synsetid TEXT,
  sentid ID,
  flag INTEGER,
  FOREIGN KEY (sentid) REFERENCES sentence(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "ruleinfo" (
       pred TEXT NOT NULL,
       lid INTEGER NOT NULL,
       rid INTEGER NOT NULL,
       flag INTEGER,
       FOREIGN KEY (lid) REFERENCES lexunit(ID) ON DELETE CASCADE ON UPDATE CASCADE,
       FOREIGN KEY (rid) REFERENCES reading(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "flag" (
    "ID" INTEGER PRIMARY KEY NOT NULL,
    "text" TEXT,
    "desc" TEXT
);

CREATE INDEX lexunit_lemma ON lexunit(lemma);
CREATE INDEX lexunit_flag ON lexunit(flag);
CREATE INDEX ruleinfo_pred ON ruleinfo(pred);
CREATE INDEX ruleinfo_lid ON ruleinfo(lid);
CREATE INDEX ruleinfo_rid ON ruleinfo(rid);

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
    (11, 'COMP_NE', 'named-entity'),
    (12, 'NOUN', 'Processed nouns'),
    (13, 'VERB', 'Processed verbs'),
    (14, 'ADJ', 'Processed adjectives'),
    (15, 'ADV', 'Processed adverbs');

INSERT INTO "corpus" ("name")
VALUES
    ('lexrules');

INSERT INTO "document" (name, corpusID)
VALUES
    ('default', (SELECT ID from "corpus" WHERE "name" = "lexrules")),
    ('processed', (SELECT ID from "corpus" WHERE "name" = "lexrules")),
    ('error', (SELECT ID from "corpus" WHERE "name" = "lexrules")),
    ('noun', (SELECT ID from "corpus" WHERE "name" = "lexrules")),
    ('verb', (SELECT ID from "corpus" WHERE "name" = "lexrules")),
    ('adj', (SELECT ID from "corpus" WHERE "name" = "lexrules")),
    ('adv', (SELECT ID from "corpus" WHERE "name" = "lexrules")),
    ('other', (SELECT ID from "corpus" WHERE "name" = "lexrules"));

INSERT INTO "corpus" ("name")
VALUES
    ('unknowns');

INSERT INTO "document" (name, corpusID)
VALUES
    ('unk_noun', (SELECT ID from "corpus" WHERE "name" = "unknowns")),
    ('unk_verb', (SELECT ID from "corpus" WHERE "name" = "unknowns")),
    ('unk_adj', (SELECT ID from "corpus" WHERE "name" = "unknowns")),
    ('unk_adv', (SELECT ID from "corpus" WHERE "name" = "unknowns")),
    ('unk_other', (SELECT ID from "corpus" WHERE "name" = "unknowns"));
