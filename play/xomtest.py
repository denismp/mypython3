#!/bin/env jython

import java.io.IOException
import nu.xom.Builder
import nu.xom.Document
import nu.xom.ParsingException

class XMLPrinter:
	"""Test the XOM library"""
	def __init__(self, URL):
		self.URL = URL

	def print_xml(self):
		try:
			parser	= nu.xom.Builder()
			doc		= parser.build( self.URL )
			print doc.toXML()
		except nu.xom.ParsingException, e:
			print self.URL + " is not well-formed."
			print e
		except java.io.IOException, e2:
			print "Unable to open " + self.URL
			print e2

def main():
	myObject = XMLPrinter( "file:///nfs/home4/dmpapp/appd4ec/etc/DAMP_UAT0000000_090504130000i.xml" )
	myObject.print_xml()

if __name__ == "__main__":
	main()
