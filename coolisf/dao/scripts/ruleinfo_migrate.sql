--
-- Script to migrate old lexrules.db to the new format
--
BEGIN TRANSACTION;

ALTER TABLE ruleinfo RENAME TO tmp_ruleinfo;

-- Add ID column, pred -> head
CREATE TABLE "ruleinfo" (
       ID INTEGER PRIMARY KEY AUTOINCREMENT,
       head TEXT NOT NULL,
       lid INTEGER NOT NULL,
       rid INTEGER NOT NULL,
       flag INTEGER,
       FOREIGN KEY (lid) REFERENCES lexunit(ID) ON DELETE CASCADE ON UPDATE CASCADE,
       FOREIGN KEY (rid) REFERENCES reading(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "rulepred" (
       ruleid INTEGER NOT NULL,
       predid INTEGER NOT NULL,
       carg TEXT,
       FOREIGN KEY (ruleid) REFERENCES ruleinfo(ID) ON DELETE CASCADE ON UPDATE CASCADE,
       FOREIGN KEY (predid) REFERENCES predinfo(ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE "predinfo" (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    pred TEXT NOT NULL UNIQUE,
    predtype INTEGER,
    lemma TEXT,
    pos TEXT,
    sense TEXT
);

-- Create index
CREATE INDEX ruleinfo_head ON ruleinfo(head);
CREATE INDEX ruleinfo_lid ON ruleinfo(lid);
CREATE INDEX ruleinfo_rid ON ruleinfo(rid);
-- predinfo
CREATE INDEX predinfo_id ON predinfo(ID);
CREATE INDEX predinfo_pred ON predinfo(pred);
CREATE INDEX predinfo_predtype ON predinfo(predtype);
CREATE INDEX predinfo_lemma ON predinfo(lemma);
CREATE INDEX predinfo_pos ON predinfo(pos);
CREATE INDEX predinfo_sense ON predinfo(sense);
CREATE INDEX rulepred_carg ON rulepred(carg);
CREATE UNIQUE INDEX rulepred_ruleid_predid_carg ON rulepred(ruleid, predid, carg);

-- Migrate old rows
INSERT INTO ruleinfo(head, lid, rid, flag)
SELECT pred, lid, rid, flag
FROM tmp_ruleinfo;

COMMIT;
