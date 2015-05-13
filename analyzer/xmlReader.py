#!/usr/bin/env python
# encoding: UTF-8

from xml.etree import ElementTree as ET 
import os

class XmlHandler:
	def __init__(self, xmlfile):
		print ("xmlHandler init: " + xmlfile)
		self.xmlTree = self.readXml(xmlfile)
	
	def readXml(self, in_path):		
		if not os.path.exists(in_path):
			print ("there is no such file: " + in_path)
			sys.exit()
		try:
			tree = ET.parse(in_path)
		except:
			print ("tree parse error")
		print ("return tree successfully")
		return tree	
	
	def getNodes(self, tree):
		root = tree.getroot()
		print ("return root successfully")
		return root.getchildren()		
		
	def findNode(self, nodes, tag):
		for node in nodes:
			if node.tag == tag:
				return node
	
	def getTexts(self, nodes, tags):
		texts = []
		for tag in tags:
			texts.append(self.findNode(nodes, tag).text)
		return texts			

	def read(self):		
		nodes = self.getNodes(self.xmlTree)
		host, port, path, timestamp, offset= self.getTexts(nodes, ["host", "port", "path", "timestamp", "offset"])
		return host, port, path, timestamp, offset
	
	def writeXml(self, node, text):
		node.text = text
		#print node.tag, node.text
	
	def setTexts(self, texts, tags):
		nodes = self.getNodes(self.xmlTree)
		for text, tag in zip(texts, tags):
			self.writeXml(self.findNode(nodes, tag), text)

	def write(self, newTimestamp, newOffset, xmlfile):
		#int "time is " + newTimestamp
		self.setTexts([newTimestamp, newOffset], ["timestamp", "offset"])
		self.xmlTree.write(xmlfile, encoding="utf-8")


if __name__ == '__main__':
	xmlHandler = XmlHandler("client_config.xml")
	print xmlHandler.read()
	#xmlHandler.write("newTimestamp", "newOffset", "client_config.xml")
	print xmlHandler.read()
