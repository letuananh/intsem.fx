#!/usr/bin/env python
# -*- coding: utf-8 -*-

from delphin.mrs.components import Pred
from util import *

# search_pred_string = lambda pred_str,extend_lemma=True: PredSense.search_pred(Pred.grammarpred(pred_str), extend_lemma) 

def main():
	print("Hello Util")
	print(PredSense.search_pred_string('have_v_1_rel', False))
	pass

if __name__ == "__main__":
	main()
