import os
##from nXmlNodeSerializer
from nodes import *

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

    
    def _get_default_tree(self):
        rootNode = Node("Settings")

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
    

def main():
    c = Configuration()
    root = c.get_root_node()
    
    if os.path.isfile(configuration_filename):
        print("file exist")
    else:
        c.save_config()
    print(root)

if __name__ == "__main__":
    main()    
