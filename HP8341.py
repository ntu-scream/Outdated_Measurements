import visa

class HP8341():

    def __init__(self):

        self.rm = visa.ResourceManager()
        self.hp = self.rm.open_resource('GPIB::19') #HP8341B GPIB address 19

        self.hp.write("IP CW6Gz PL-10dB") #Set RF output to 6GHz and -10dBm

    def __str__(self):
        return "initialized"

    def setFrequency(self, frequency):
        self.hp.write("CW %f Gz" %frequency) #Set RF frequency, in GHz
        print("RF frequency:%f GHz" %frequency)

    def setPower(self, power):
        self.hp.write("PL %f dB" %power) #Set RF power level, in dBm
        print("RF power:%f dBm" %power)
        

if __name__ == '__main__':
    
    new = HP8341()

    new.setPower(10) #Set power to 10dBm
    
    i=5
    while i<=12:
        new.setFrequency(i) #Sweep frequency from 5GHz to 12 GHz
        i+=1
        
    print(new)
