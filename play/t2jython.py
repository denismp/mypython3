#!/bin/env jython
from xml.etree import ElementTree as ET

print "Here I am too."

tree = ET.parse("page.xhtml")

# the tree root is the toplevel html element
print tree.findtext("head/title")

# if you need the root element, use getroot
root = tree.getroot()

# ...manipulate tree...

tree.write("out.xml")
