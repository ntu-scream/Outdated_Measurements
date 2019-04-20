import visa

class Keithley:
    
    def __init__(self, func):
        self.rm = visa.ResourceManager()
        #Depending on instrument GPIB address
        self.keithley = self.rm.open_resource('GPIB::16')
        #For K2000, GPIB address is 16
        #Reset K2000
        self.keithley.write("*rst; status:preset; *cls") #Reset K2000
        #set mode
        self.keithley.write("configure:%s" % func) 
        #self.keithley.write("status:measurement:enable 512; *sre 1")
        #self.keithley.write("trigger:source bus")
        #self.keithley.write("trace:feed sense1; feed:control next")
        #Prepare K2000 for trigger
        self.keithley.write("initiate")

        print("initialized")
    def __str__(self):
        return "initialized"


    def measureOnce(self):
        #self.keithley.assert_trigger()
        #self.keithley.wait_for_srq()
        #Request data from K2000
        result=[0.0]
        #raw= self.keithley.query_ascii_values("trace:data?")
        raw = self.keithley.query_ascii_values("READ?")
        #Reset Keithley
        #self.keithley.query("status:measurement?")
        #self.keithley.write("trace:clear; feed:control next")
        for i in raw:
            result.append(float(i))
        return result

    def measureMulti(self,average):

        i=1
        data=0
        N=average #Number of averages

        while i<=N:
            tmp=self.keithley.query_ascii_values("READ?")
            data=data+tmp[0]
            i+=1
            
        return float(data/average)

 
    def measurement(self):
        
        #Setup measurement
    
        self.keithley.write("configure:%s" % self.func) 
        self.keithley.write("status:measurement:enable 512; *sre 1")
        self.keithley.write("sample:count %d" % self.number_of_readings)
        #self.keithley.write("sample:count 1")
        self.keithley.write("trigger:source bus")
        #self.keithley.write("trigger:delay %f" % (self.interval_in_ms / 1000.0))
        #self.keithley.write("trigger:delay 10")
        #self.keithley.write("trace:points %d" % self.number_of_readings)
        self.keithley.write("trace:feed sense1; feed:control next")
        #Prepare K2000 for trigger
        self.keithley.write("initiate")
        self.keithley.assert_trigger()
        self.keithley.wait_for_srq()
        #Request data from K2000
        self.result = self.keithley.query_ascii_values("trace:data?")
        #self.result = self.keithley.query(":READ?")
        #average = 0;
        #for i in self.result:
           # self.average += int(i)
        #self.average /= len(self.result)
        #Reset Keithley
        self.keithley.query("status:measurement?")
        self.keithley.write("trace:clear; feed:control next")
             


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

 
if __name__ == '__main__':
    
    print()
 
