#! /bin/env jython
import org.jdom as jdom
import java.io as io

def printDocument( jdomDoc ):
	print "Printing..."
	rootElement = jdomDoc.rootElement
	iter = rootElement.getDescendants()
	print dir( iter )
	while iter.hasNext():
		element = iter.next()
		#print type( element )
		#print dir( element )
		if isinstance( element, jdom.Text ):
			print "textTrim=" + element.textTrim
		if isinstance( element, jdom.Element ):
			#print "element=" + str( dir( element ) )
			print "element=" + element.getName()


if __name__ == "__main__":
	builder = jdom.input.SAXBuilder()
	doc		= builder.build( io.FileInputStream( "/nfs/home4/dmpapp/appd4ec/tmp/QAMP_UAT0000000_090504130000i.xml" ) )
	printDocument( doc )
