intsem.fx
=========

Integrated semantic framework

1. Check out beautifulsoup, pydelphin and nltk to ~/workspace folder 

git clone https://github.com/letuananh/beautifulsoup.git ~/workspace/beautifulsoup 
git clone https://github.com/nltk/nltk.git ~/workspace/nltk
git clone https://github.com/goodmami/pydelphin.git ~/workspace/pydelphin

2. Check out the code of intsem.fx to ~/workspace with:
```
git clone --recursive https://github.com/letuananh/intsem.fx.git
```

The longer verion of the command above is:
```
git clone https://github.com/letuananh/intsem.fx.git
cd intsem.fx
git submodule init
git submodule update
```

3. Check out ERG to your workspace folder and compile the grammar

This is complicated, read more here: http://moin.delph-in.net/TuanAnhLe/GramEng4Dummies

Basically, I need the grammar file (erg.dat) to be located at ~/workspace/erg/erg.at

4. Configure the application
```
cd ~/workspace/intsem.fx
./config.sh
```