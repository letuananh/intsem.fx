#!/usr/bin/env pythons
# -*- coding: utf-8 -*-

from ergpreds import ERG_PRED_MAP as EPM

def main():
	rel = '_dog_n_1_rel'
	if rel in EPM:
		for sense in EPM[rel]:
			print(sense)
	pass

if __name__ == "__main__":
	main()
