import visa

class Keithley2400:
    
    def __init__(self, func):
        self.rm = visa.ResourceManager()
        #Depending on instrument GPIB address
        self.keithley2400 = self.rm.open_resource('GPIB::20')
        #For K2400, GPIB address is 20
        #Reset K2400
        self.keithley2400.write("*rst; status:preset; *cls") #Reset K2400
        self.keithley2400.write(":SYST:BEEP:STAT OFF") #Beep off
        self.keithley2400.write(":SYST:RSEN OFF") #2-wire:OFF / 4-wire:ON

        print("initialized")

    def __str__(self):
        return "initialized"

    def fourWireOn(self):
        self.keithley2400.write(":SYST:RSEN ON") #2-wire:OFF / 4-wire:ON

    def fourWireOff(self):
        self.keithley2400.write(":SYST:RSEN OFF") #2-wire:OFF / 4-wire:ON

    def outputOn(self):
        self.keithley2400.write(":OUTPUT ON")
        print("Keithley2400 output: ON")

    def outputOff(self):
        self.keithley2400.write(":OUTPUT OFF")
        print("Keithley2400 output: OFF")

    def setCurrent(self, current):

        #Note that above 20mA will kill the extended film device!
        self.keithley2400.write(":SOUR:FUNC CURR")
        self.keithley2400.write(":SOUR:CURR:MODE FIX")
        self.keithley2400.write(":SOUR:CURR:RANG 1e-1") #set range to 100mA
        
        I = current/1000 #convert to mA
        self.keithley2400.write(":SOUR:CURR:LEV %f" %I)
        print("Keithley2400 current set to: %f mA" %current)

    def measureOnce(self):
        self.keithley2400.write("initiate")
        #Sensing with voltage, protected by default compliance ~ 21V
        self.keithley2400.write(":SENS:FUNC 'VOLT'")
        self.keithley2400.write(":SENS:VOLT:PROT 200")
        self.keithley2400.write(":SENS:VOLT:RANG 100") 
        #Request data from K2400
        result=[0.0]
        #raw= self.keithley.query_ascii_values("trace:data?")
        raw= self.keithley2400.query_ascii_values("READ?")
        for i in raw:
            result.append(float(i))
        return result
 
    def measurement(self):
        
        #Setup measurement
    
        self.keithley2400.write("configure:%s" % self.func) 
        self.keithley2400.write("status:measurement:enable 512; *sre 1")
        self.keithley2400.write("sample:count %d" % self.number_of_readings)
        #self.keithley2400.write("sample:count 1")
        self.keithley2400.write("trigger:source bus")
        self.keithley2400y.write("trace:feed sense1; feed:control next")
        #Prepare K2400 for trigger
        self.keithley2400.write("initiate")
        self.keithley2400.assert_trigger()
        self.keithley2400.wait_for_srq()
        #Request data from K2400
        self.result = self.keithley2400.query_ascii_values("trace:data?")
        #Reset Keithley
        self.keithley2400.query("status:measurement?")
        self.keithley2400.write("trace:clear; feed:control next")
             
    def save(self, s):
        result = ""
        for i in s:
            if i in self.code:
                j = self.alph.index(i)
                result += self.code[j]
            else:
                result += i
     
        return result
     
    def toDecode(self, s):
        result = ""
        for i in s:
            if i in self.code:
                j = self.code.index(i)
                result += self.alph[j]
            else:
                result += i
     
        return result

    def pulse(self,current, current_max,trigger_delay,source_delay):

        self.keithley2400.write(":SOUR:FUNC CURR")  #source current
        self.keithley2400.write(":SOUR:CURR %f"%(current*0.001)) #source current level in A
        self.keithley2400.write(":TRIG:DEL %d"%trigger_delay)

        self.keithley2400.write(":SOUR:DEL %g"%source_delay)
        self.keithley2400.write(":TRAC:FEED:CONT NEXT")
        self.keithley2400.write(":SOUR:CLE:AUTO ON")  #source auto clear
        self.keithley2400.write(":INIT")

    def voltage_pulse(self,voltage, voltage_max,trigger_delay,source_delay):

        self.keithley2400.write(":SOUR:FUNC VOLT") #source voltage
        self.keithley2400.write(":SENS:CURR:PROT 10E-3") #set10mA compliance
        self.keithley2400.write("TRIG:COUN 1") #sets to send just one pulse
        self.keithley2400.write("SOUR:VOLT %f"%(voltage))
        self.keithley2400.write(":TRIG:DEL %d"%trigger_delay)
        self.keithley2400.write(":SOUR:DEL %g"%source_delay)
        self.keithley2400.write(":TRAC:FEED:CONT NEXT")
        self.keithley2400.write(":SOUR:CLE:AUTO ON")  #source auto clear
        self.keithley2400.write(":INIT")

    # sets the device to 200 kOhm (10 uA, 2.1 V) resistance mode to avoid burning device when probes are moved
    def minimize(self):
        self.keithley2400.write(":SENS:FUNC 'RES'") # set to resistance measurement
        self.keithley2400.write(":RES:MODE AUTO") # set at auto mode
        self.keithley2400.write(":RES:RANG 20E4") # set to 200 kOhm mode (10 uA)


if __name__ == '__main__':
    
    print()
    new = Keithley2400()
    new.pulse( current_max= 10, trigger_delay=0.1, source_delay=0.1)
 
