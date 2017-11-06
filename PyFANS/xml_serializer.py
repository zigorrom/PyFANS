from PyQt4 import QtXml
from nodes import *

class XmlNodeSerializer():
    def __init__(self):
        t = Node
        self.typeDic = dict((cls.typeInfo(),(cls, self.requiredNodeAttributes(cls))) for cls in t.__subclasses__())
        self.typeDic[t.typeInfo()] = (t, self.requiredNodeAttributes(t))
        

    def serialize(self,rootNode):
        doc = QtXml.QDomDocument()
        xmlNode = self.xmlFromNode(doc,rootNode)
        doc.appendChild(xmlNode)
        for child in rootNode._children:
            self._recurseXml(doc, xmlNode,child)
        return doc.toString(indent = 4)

    def _recurseXml(self, doc, parentXmlNode,node):
        xmlNode = self.xmlFromNode(doc,node)
        parentXmlNode.appendChild(xmlNode)
        for child in node._children:
            self._recurseXml(doc,xmlNode,child)

    def xmlFromNode(self,doc, node):
        key = node.typeInfo()
        xmlNode = doc.createElement(key)
        cls, attrs = self.typeDic[key]
        for k, v in attrs.items():
            val = v.fget(node)
            if type(val) is bool:
                val = "bool:{0}".format("True" if val else "False")

            elif type(val) is int:
                val = "i:{0}".format(val)

            elif type(val) is float:
                val = "f:{0}".format(val)
##            res = val
            elif type(val) is list:
                val = "list:[{0}]".format(",".join(val))
            xmlNode.setAttribute(k, val)
        return xmlNode
        


    def requiredNodeAttributes(self, nodeType):
        requiredAttributes = {}
        for cls in nodeType.__mro__:
            for k,v in cls.__dict__.items():
                if isinstance(v,property):
                    requiredAttributes[k] = v
        return requiredAttributes
    
    def nodeFromXml(self,domElement):
        key = domElement.tagName()
        cls, attrs = self.typeDic[key]
        node = cls("unknown")
        counter = 0
        for k,v in attrs.items():
            if domElement.hasAttribute(k):
                if v.fset is not None:
                    val = domElement.attribute(k)
                    print("name: {0}, val: {1}, type: {2}".format(k,val,type(val)))
                    
                    if val.startswith("bool:"):
                        val = val[5:] #bool(val[6:])
                        print(val)
                        print(len(val))
                        print(val == "True")
                        val = (True if val == "True" else False)

                    elif val.startswith("i:"):
                        val = int(val[2:])

                    elif val.startswith("f:"):
                        val = float(val[2:])

                    elif val.startswith("list:[") and val.endswith("]"):
                        val = val[6:-1]
                        val = val.split(",")
                    print("converted value: {0}, type:{1}\n".format(val, type(val)))
                    v.fset(node,val)
            counter+=1
        return node

        
    def deserialize(self, xmlString):
        xml = QtXml.QDomDocument()
        if not xml.setContent(xmlString):
            print("failed")
            raise ValueError()
        
        xmlRootNode = xml.documentElement()
        rootNode = self.nodeFromXml(xmlRootNode)
        self.build_tree(xmlRootNode,rootNode)
        return rootNode
    
    def build_tree(self, parentXmlNode, parentNode=None, tabLevel=-1):
        key = parentXmlNode.tagName()
        tabLevel += 1
##        print("{0}|------ {1}\n".format("\t"*tabLevel,key))
##        print(parentNode)
        xmlChildNode = parentXmlNode.firstChild()        
        while not xmlChildNode.isNull():
            xmlElement = xmlChildNode.toElement()
            if not xmlElement.isNull():
                node = self.nodeFromXml(xmlElement)
                if parentNode is not None:
                    parentNode.addChild(node)
                
                self.build_tree(xmlElement,parentNode = node,tabLevel=tabLevel)
            xmlChildNode = xmlChildNode.nextSibling()
        tabLevel -=1 
