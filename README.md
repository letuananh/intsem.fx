Integrated Semantic Framework (intsem.fx)
=========

# Prerequisite

* Python >= 3.5
* Required packages (see requirements.txt)
* English Resource Grammar (rev >= 26135)
* NLTK data
* LeLESK data (see https://github.com/letuananh/lelesk)

# Installation

* Download and install ACE >= 0.9.26 from: http://sweaglesw.org/linguistics/ace/
* Download ERG trunk from SVN `svn checkout http://svn.delph-in.net/erg/trunk`
* Build erg.dat `ace -g ace/config.tdl -G erg.dat`
* Download the latest release from: https://github.com/letuananh/intsem.fx/releases, unzip it to a folder and run the `isf` command
* Download NLTK data
```
import nltk
nltk.download("book")
```


Tips:
`pip` is recommended for installing required packages
```
python -m pip install -r requirements.txt
```


# Using ISF

```
cd ~/workspace/intsem.fx
./isf parse data/sample.txt data/sample.out
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

Notes:

Use virtualenv to install required packages
```
python3 -m venv ~/isf_py3
. ~/isf_py3/bin/activate
```

Install these packages if you are using Fedora Linux:
```
sudo dnf install -y redhat-rpm-config gcc-c++
```
