from nodes import *


def get_default_tree():
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
    root = get_default_tree()
    print(root)

if __name__ == "__main__":
    main()    
