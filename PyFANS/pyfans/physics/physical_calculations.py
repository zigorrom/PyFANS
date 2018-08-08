import math

def calculate_thermal_noise(equivalent_resistance, sample_resistance, load_resistance, temperature, amplifier_input_resistance = 1000000):
        equivalent_resistance = math.fabs(equivalent_resistance)
        sample_resistance = math.fabs(sample_resistance)
        load_resistance = math.fabs(load_resistance)
        #equivalent_resistance = math.fabs(equivalent_resistance)
        amplifier_input_resistance = math.fabs(amplifier_input_resistance)
        equivalent_resistance = (equivalent_resistance * amplifier_input_resistance) / (equivalent_resistance + amplifier_input_resistance)
        room_temperature = 297
        # temperature = room_temperature if not temperature else temperature
        kB = 1.38064852e-23
        equivalent_load_resistance =  (load_resistance + amplifier_input_resistance) / (load_resistance * amplifier_input_resistance)
        thermal_noise = 4*kB * (temperature/sample_resistance + room_temperature*equivalent_load_resistance) * equivalent_resistance*equivalent_resistance 
        return thermal_noise

