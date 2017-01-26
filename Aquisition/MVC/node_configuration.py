import os
##from nXmlNodeSerializer
from nodes import *
from xml_serializer import XmlNodeSerializer
configuration_filename = "config.xml"

class Configuration(object):
    def __init__(self):
        self.rootNode = None
        fileExist = self._config_file_exist()
        if fileExist:
            print("reading file")
            self.rootNode = self._read_config_file()
        else:
            print("default tree")
            self.rootNode = self._get_default_tree()
        
    def get_root_node(self):
        return self.rootNode

    def save_config(self):
        self._write_config_file()
    
    def _config_file_exist(self):
        return os.path.isfile(configuration_filename)

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
        print(relativeRoot)
            
        if relativeRoot is None:
            return None

        if path_length == 1:
            return relativeRoot

        node = self._find_target_node_by_path_from_relative_node(relativeRoot,path_list)

        return node
            
    
    def _get_default_tree(self):
        rootNode = Node("Settings")
        ##Settings
        acq_settings = AcquisitionSettingsNode("acquisition_settings",parent = rootNode)
        NumericNode("sample_rate", parent = acq_settings)
        NumericNode("points_per_shot", parent = acq_settings)
        CheckNode("homemade_amplifier", parent = acq_settings)
        ComboNode("pga_gain",parent = acq_settings)
        ComboNode("filter_gain", parent = acq_settings)
        ComboNode("filter_cutoff",parent = acq_settings)



        inp_settings = Node("input_settings", parent = rootNode)

        ch1 = InChannelNode("ch1",inp_settings)
        CheckNode("enabled", parent = ch1)
        ComboNode("range", case_list=['One','Two','Three'], parent = ch1)
        ComboNode("polarity",case_list=['Unipolar','Bipolar'],parent = ch1)
        ComboNode("function",case_list=['Vds','Vlg','Vbg'],parent=  ch1)


        ch2 = InChannelNode("ch2",inp_settings)
        CheckNode("enabled", parent = ch2)
        ComboNode("range", case_list=['One','Two','Three'], parent = ch2)
        ComboNode("polarity",case_list=['Unipolar','Bipolar'],parent = ch2)
        ComboNode("function",case_list=['Vds','Vlg','Vbg'],parent=  ch2)


                
        ch3 = InChannelNode("ch3",inp_settings)
        CheckNode("enabled", parent = ch3)
        ComboNode("range", case_list=['One','Two','Three'], parent = ch3)
        ComboNode("polarity",case_list=['Unipolar','Bipolar'],parent = ch3)
        ComboNode("function",case_list=['Vds','Vlg','Vbg'],parent=  ch3)



        ch4 = InChannelNode("ch4",inp_settings)
        CheckNode("enabled", parent = ch4)
        ComboNode("range", case_list=['One','Two','Three'], parent = ch4)
        ComboNode("polarity",case_list=['Unipolar','Bipolar'],parent = ch4)
        ComboNode("function",case_list=['Vds','Vlg','Vbg'],parent=  ch4)

        out_settings = Node("out_settings", parent = rootNode)

        och1 = OutChannelNode("och1",out_settings)
        CheckNode("enabled", parent = och1)
        ComboNode("range", parent = och1)
        ComboNode("polarity",parent = och1)
        ComboNode("out_pin",parent = och1)
        ComboNode("function",parent=  och1)


        och2 = OutChannelNode("och2",out_settings)
        CheckNode("enabled", parent = och2)
        ComboNode("range", parent = och2)
        ComboNode("polarity",parent = och2)
        ComboNode("out_pin",parent = och2)
        ComboNode("function",parent=  och2)

        return rootNode

    def set_binding(self,path, property_name,callback):
        node = self.get_node_from_path(path)
        if node is not None:
            node.addObserver(property_name,callback)

            

def name_changed(value):
    print("from callback {0}".format(value))

def main():
    c = Configuration()
    root = c.get_root_node()
    print(root)
    path = "ch1.enabled"
    c.set_binding(path,"name",name_changed)
##    c.set_binding(path,"name",name_changed)
    node = c.get_node_from_path(path)
##    node.addObserver("name",name_changed)
    print(node)
    node.name = "asfgashfglkgkg"
    print("_________")
    print(node)
##    if os.path.isfile(configuration_filename):
##        print("file exist")
##    else:
##        c.save_config()
    

if __name__ == "__main__":
    main()    
