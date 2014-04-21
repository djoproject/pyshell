#!/usr/bin/python
# -*- coding: utf-8 -*-

class injectTest(unittest.TestCase):
	pass
	
	#_getTheIndexWhereToStartTheSearch(self,processType)
		#FAIL
			#try a value different of pre/pro/post process

		#SUCCESS
			#if stack empty return zero
			#three different type on stack, search each of them
			#search for each type when they are missing on stack


	#_findIndexToInjectPre(self, cmdPath)
		#FAIL
			#invalid path length
			#invalid sub index
			

		#SUCCESS
			#make a perfect match
			#make a perfect match except for the last sub index
			#no match

			#only one match on stack
			#several match on stack

			#at the botom of the stack
			#or with different path under the current path (higher path ?)
		
	#_findIndexToInjectProOrPost(self, cmdPath, processType)
		#FAIL
			#try to inject preprocess
			#try to inject pro process with non root path
			#try to find to big cmdPath, to generate invalid index
			#try to find path with invalid sub index

		#SUCCESS
			#with 0, 1 or more item of each type
			#with existing path, or inexsting path
		
	#injectDataProOrPos(self, data, cmdPath, processType, onlyAppend = False)
		#FAIL
			#try to insert unexistant path with onlyAppend=True

		#SUCCESS
			#insert existant or not
			#post or pro
		
	#_injectDataPreToExecute(self, data, cmdPath, index, enablingMap = None, onlyAppend = False)
		#FAIL
			#map of invalid length (!= of path)
			#onlyAppend=True and inexistant path
			#onlyAppend=True and existant path and different map

		#SUCCESS
			#insert unexisting
			#insert existing with path matching
			#insert existing whitout path matching

			#test with index 0 or -1
		
	#injectDataPre(self, data, cmdPath, enablingMap = None)
		#FAIL
			#insert existant path but with inexistant map

		#SUCCESS
			#insert existant path with existant map
				#in the beginning, in the middle or at the end of the existant
			#insert inexistant path
		
	#insertDataToPreProcess(self, data, onlyForTheLinkedSubCmd = True)
		#FAIL
			#TODO

		#SUCCESS
			#TODO
		
	#insertDataToProcess(self, data)
		#FAIL
			#TODO

		#SUCCESS
			#TODO
		
	#insertDataToNextSubCommandPreProcess(self,data)
		#FAIL
			#TODO

		#SUCCESS
			#TODO

if __name__ == '__main__':
    unittest.main()
