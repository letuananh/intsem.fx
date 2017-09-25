Integrated Semantic Framework (intsem.fx)
=========

1 - Prerequisite

* Python >= 3.5
* Required packages (see requirements.txt)
* English Resource Grammar (rev >= 26135)
* NLTK data
* LeLESK data (see https://github.com/letuananh/lelesk)

# Installation

* Download the latest release from: https://github.com/letuananh/lelesk/releases, unzip it to a folder and run the `isf` command

```
cd ~/workspace/intsem.fx
./isf parse data/sample.txt data/sample.out
```
Tips: `pip` is recommended for installing required packages
```
cd ~/workspace/intsem.fx
pip install -r requirements.txt
```


# Development

WARNING: These are meant for developers who want to contribute to the codebase. If all you need is to run the ISF to process your data, please see the Installation section above instead.

2 - Check out the code of intsem.fx to ~/workspace with:

```
git clone --recursive https://github.com/letuananh/intsem.fx.git
```

3 - Check out ERG to your workspace folder and compile the grammar

This is complicated, read more here: http://moin.delph-in.net/TuanAnhLe/GramEng4Dummies

Basically, I need the grammar file (erg.dat) to be located at ~/workspace/cldata/erg.dat

4 - Configure the application
```
cd ~/workspace/intsem.fx
./config.sh
```
To use ISF, please try
```
cd ~/workspace/intsem.fx
./isf --help
```
