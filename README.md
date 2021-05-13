# Integrated Semantic Framework (intsem.fx)

A Python 3 implementation of the [Integrated Semantic Framework](https://osf.io/9udjk/) that provides computational deep semantic analysis by combining structural semantics from construction grammars and lexical semantics from ontologies in a single representation.

`coolisf` is only a back-end semantic parsing module that runs on command-line interaface or in Python programs.
If you want a friendly graphical user interface, please use [visualkopasu](https://github.com/letuananh/visualkopasu/).

# A quick glance

To parse a sentence, use coolisf `text` command

```bash
python -m coolisf text "I drink green tea." -f dmrs

:`I drink green tea.` (len=5)
------------------------------------------------------------
dmrs {
  10000 [pron<0:1> x ind=+ num=sg pers=1 pt=std];
  10001 [pronoun_q<0:1> x ind=+ num=sg pers=1 pt=std];
  10002 [_drink_v_1_rel<2:7> e mood=indicative perf=- prog=- sf=prop tense=pres];
  10003 [udef_q<8:18> x num=sg pers=3];
  10004 [_green+tea_n_1_rel<8:18> x num=sg pers=3];
  0:/H -> 10002;
  10001:RSTR/H -> 10000;
  10002:ARG1/NEQ -> 10000;
  10002:ARG2/NEQ -> 10004;
  10003:RSTR/H -> 10004;
}
# 10002 -> 01170052-v[drink/lelesk]
# 10004 -> 07935152-n[green tea/lelesk]
...
```

For batch processing, create a text file with each sentence on a separate line.
For example here is the content of the file `sample.txt`

```
I drink green tea.
Sherlock Holmes has three guard dogs.
A soul is not a living thing.
Do you have any green tea chest?
```

After that, run the following command and the output will be written to the file `demo_out.xml`

```bash
python -m coolisf parse demo.txt -o demo_out.xml
```

In Python code

```python
from coolisf import GrammarHub
ghub = GrammarHub()
# parse an English text
sent = ghub.ERG_ISF.parse("I love drip coffee.")
# print semantic structures for all potential readings
for reading in sent:
    print(reading.dmrs())
```

Output

```bash
dmrs {
  10000 [pron<0:1> x ind=+ num=sg pers=1 pt=std];
  10001 [pronoun_q<0:1> x ind=+ num=sg pers=1 pt=std];
  10002 [_love_v_1_rel<2:6> e mood=indicative perf=- prog=- sf=prop tense=pres];
  10003 [udef_q<7:19> x num=sg pers=3];
  10004 [_drip+coffee_n_1_rel<7:19> x num=sg pers=3];
  0:/H -> 10002;
  10001:RSTR/H -> 10000;
  10002:ARG1/NEQ -> 10000;
  10002:ARG2/NEQ -> 10004;
  10003:RSTR/H -> 10004;
}
...
```

# Install

`coolisf` only works on Linux distributions at the moment (built and tested on Fedora and Ubuntu Linux). 

- Install `coolisf` package from [PyPI](https://pypi.org/project/coolisf/) using pip

```
pip install coolisf
```

- Create coolisf data folder at `/home/user/local/isf/data`
- Download ace-0.9.26 binary from https://osf.io/x52fy/ to `/home/user/bin/ace`. Make sure that you can run ace by

```bash
[isf]$ ~/bin/ace -V
ACE version 0.9.26
compiled at 18:48:50 on Sep 14 2017
```

- Install [lelesk](https://pypi.org/project/lelesk/) and yawlib with data
- Download coolisf lexical rules database from https://osf.io/qn4wz/ and extract it to `/home/user/local/isf/data/lexrules.db`
- Download grammar files (erg.dat, jacy.dat, virgo.dat, etc.) and copy them to `/home/user/local/isf/data/grammars/`

The final data folder should look something like this

```
/home/user/local/isf/data
├── grammars
│   ├── erg.dat
│   └── jacy.dat
├── lexrules.db
```

If you encounter any problems or difficulties, please submit a ticket for support at: https://github.com/letuananh/intsem.fx/issues
