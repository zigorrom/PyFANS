import os
from PyQt4 import QtCore
##from nXmlNodeSerializer
from nodes import Node, ExperimentSettings, ValueRange, HardwareSettings
from xml_serializer import XmlNodeSerializer

configuration_filename = "config.exp"

class Configuration(object):
    
    def __init__(self, text = None):

        self.rootNode = None
        if text:
            print("configuration from variable")
            self.rootNode = self._load_config_text(text)

        elif self._config_file_exist():
            print("reading file")
            self.rootNode = self._read_config_file()
        else:
            print("default tree")
            self.rootNode = self._get_default_tree()
        #self.rootNode = self._get_default_tree()

        
    def get_root_node(self):
        return self.rootNode

    def save_config(self):
        self._write_config_file()
    
    def _config_file_exist(self):
        return os.path.isfile(configuration_filename)

    def _load_config_text(self,text):
        if text:
            serializer = XmlNodeSerializer()
            node = serializer.deserialize(text)
            return node

    def _read_config_file(self):
        with open(configuration_filename,"r") as cfg:
            text = cfg.read()
            serializer = XmlNodeSerializer()
            node = serializer.deserialize(text)
            return node
            
##        return "from file"
    
    
    def _write_config_file(self):
        if self.rootNode is not None:
            with open(configuration_filename,"w") as cfg:
                serializer = XmlNodeSerializer()
                text = serializer.serialize(self.rootNode)
                cfg.write(text)

##  Setings.acquisition_settings.sample_rate
##  or
##  .acquisirion_settings.sample_rate
##  or
##  .sample_rate                
##
    

    def get_node_from_path(self, path):
        path_list = path.split(".")
        print(path_list)
        node = self._traverse_tree(path_list)
        return node

    def _fing_current_node(self,root_node, node_name):
        if node_name == root_node.name:
            return root_node
        else:
            for i in range(root_node.childCount()):
                node = self._fing_current_node(root_node.child(i),node_name)
                if node is not None:
                    return node
        
    def _find_target_node_by_path_from_relative_node(self, rootNode, path_list):
        length = len(path_list)
        if length < 2:
            return rootNode
        
        path_count = 1
        node_found = False
        currentNode = rootNode
        while not node_found:
            if path_count >= length:
                return currentNode
            
            node = currentNode.getChildByName(path_list[path_count])
            if node is None:
                return None
            else:
                currentNode = node
                path_count+=1
        
            
    def _traverse_tree(self, path_list):
        path_length =len(path_list)
        if path_length < 1:
            return None
        root = self.rootNode
        relativeRoot = self._fing_current_node(root,path_list[0])
        #print(relativeRoot)
            
        if relativeRoot is None:
            return None

        if path_length == 1:
            return relativeRoot

        node = self._find_target_node_by_path_from_relative_node(relativeRoot,path_list)

        return node
            
    
        
    def _get_default_tree(self):
        rootNode = Node("Settings")
        ##Settings
        settings = ExperimentSettings("ExperimentSettings",parent = rootNode)
        drain_source_range = ValueRange("drain_source_range",settings)
        gate_source_range = ValueRange("front_gate_range",settings)

        hardware_settings = HardwareSettings("HardwareSettings", parent = rootNode)

        return rootNode

    def set_binding(self,path, property_name,callback):
        node = self.get_node_from_path(path)
        if node is not None:
            node.addObserver(property_name,callback)

            

def name_changed(value,sender):
        
        print("from callback {0}".format(value))

def initialized():
    print("initialized")

def main():
    c = Configuration()
    
    root = c.get_root_node()
    print(root)
    path = "input_settings.ch1"
##    c.set_binding(path,"name",name_changed)
    c.set_binding(path,"name",name_changed)
    node = c.get_node_from_path(path)
##    node.addObserver("name",name_changed)
    print(node)
    node.name = "asfgashfglkgkg"
    #print("_________")
    #print(node)
##    if os.path.isfile(configuration_filename):
##        print("file exist")
##    else:
##        c.save_config()
    

if __name__ == "__main__":
    main()    
