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
			#print doc.toXML()
			rootEl	= doc.getRootElement()
			#result	= rootEl.query( "/applicationUpdateProperties/updateParameters/ccid" )
			result	= rootEl.query( "/applicationUpdateProperties" )
			print type( result )
			nodeCount = result.size()
			print "nodeCount=" + str( nodeCount )
			childCount = 0
			cnode	= None
			for i in range( 0, nodeCount ):
				cnode = result.get( i )
				print type( cnode )
				childCount = cnode.getChildCount()
				print "childCount=" + str( childCount )
				#nodedoc = cnode.getDocument()
				#print "value=" + nodedoc.getValue()
			#child = cnode.getChild( 0 )
			#print "child value=" + child.getValue()
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
