import time

class DnsAnalysis :
    def __init__(self,bits):
        self.bit = bits
        i = 12
        while 1:
            count = self.bit[i]
            i += count + 1
            if self.bit[i] == 0:
                break
        self.QNAMECOUNT = i

    def Debug(self):
        hexdata = []
        for i in self.bit:
            hexdata.append(hex(i))
        i = 0
        tt = ""
        while i < len(hexdata) :
            for  kk in hexdata[i : i + 12] :
                if len(str(kk)) <= 3 :
                    tt += "0" + str(kk)[2:] + " "
                else :
                    tt += str(kk)[2:]+" "
            tt += "\n"
            i += 12
        return tt

    def ID(self):
        idd = self.bit[0:2]
        return int.from_bytes(idd, byteorder='big')

    def QR(self):
        byte = self.bit[2]
        byte = byte >> 7
        return byte

    def Qpcode(self):
        byte = self.bit[2]
        byte = byte & 127
        byte = byte >> 3
        return byte

    def AA(self):
        byte = self.bit[2]
        byte = byte & 4
        byte = byte >> 2
        return byte

    def TC(self):
        byte = self.bit[2]
        byte = byte & 2
        byte = byte >> 1
        return byte

    def RD(self):
        byte = self.bit[2]
        byte = byte & 1
        return byte

    def RA(self):
        byte = self.bit[3]
        byte = byte >> 7
        return byte

    def Z(self):
        byte = self.bit[3]
        byte = byte & 127
        byte = byte >> 4
        return byte

    def RCODE(self):
        byte = self.bit[3]
        byte = byte & 15
        return byte

    def QDCOUNT(self):
        qd_count = self.bit[4:6]
        return int.from_bytes(qd_count, byteorder='big')

    def ANCOUNT(self):
        AN_count = self.bit[6:8]
        return int.from_bytes(AN_count, byteorder='big')

    def NSCOUNT(self):
        NS_count = self.bit[8:10]
        return int.from_bytes(NS_count, byteorder='big')

    def ARCOUNT(self):
        AR_count = self.bit[10:12]
        return int.from_bytes(AR_count, byteorder='big')


    def QNAME(self):
        i = 12
        stra = ""
        while 1:
            count = self.bit[i]
            stra += self.bit[i + 1:i + 1 + count].decode('ascii')
            i += count + 1
            if self.bit[i] == 0:
                break
            else:
                stra += '.'
        return stra

    def QTYPE(self):
        return int.from_bytes(self.bit[self.QNAMECOUNT + 1:self.QNAMECOUNT + 3], byteorder='big')

    def QCLASS(self):
        return int.from_bytes(self.bit[self.QNAMECOUNT + 3:self.QNAMECOUNT + 5], byteorder='big')

    
    def printall(self):
        return "ID:" + str(self.ID()) + "\tQR:" + str(self.QR()) + "\tQpcode:" + str(self.Qpcode()) \
               + "\tAA:" + str(self.AA()) + "\tTC:" + str(self.TC() )+ "\tRD:" + str(self.RD()) + "\tRA:" + str(self.RA()) \
               + "\tZ:" + str(self.Z()) + "\nRCODE" + str(self.RCODE()) + "\tQDCOUNT" + str(self.QDCOUNT()) \
               + "\tANCOUNT:" + str(self.ANCOUNT()) + "\tNSCOUNT:" + str(self.NSCOUNT()) + "\tARCOUNT:" + str(self.ARCOUNT()) \
               + "\tADRESS:" + self.QNAME() + "\tQTYPE:" + str(self.QTYPE()) + "\tQCLASS" + str(self.QCLASS())


class DnsCreate :
    def __init__(self, bits):
        self.bit = bits
        i = 12
        while 1:
            count = self.bit[i]
            i += count + 1
            if self.bit[i] == 0:
                break
        self.QNAMECOUNT = i
        self.bitList = []
        for i in self.bit :
            self.bitList.append(i)




    def setID(self,ID):
        self.bitList[0] = (ID & 65280) >> 8
        self.bitList[1] = (ID & 255)

    def setQR(self,QR):
        if QR == 1 :
            self.bitList[2] = self.bitList[2] |  128
        else:
            self.bitList[2] = self.bitList[2] & 127

    def setRCODE(self, data):
        data = data & 15
        self.bitList[3] = self.bitList[3] & 240
        self.bitList[3] = self.bitList[3] | data

    def setRDATA(self,data):
        self.bitList[7] = 1

        i = 12
        while i < self.QNAMECOUNT + 1:
            self.bitList.append(self.bit[i])
            i = i + 1

        self.bitList.append(0)
        self.bitList.append(1)

        self.bitList.append(0)
        self.bitList.append(1)

        self.bitList.append(0)
        self.bitList.append(0)
        self.bitList.append(0)
        self.bitList.append(120)

        self.bitList.append(0)
        self.bitList.append(4)

        for i in data :
            self.bitList.append(i)

    def GetBytes(self):
        return bytes(self.bitList)


class AdressList :
    def __init__(self,fileName):
        self.file = open(fileName,'r')
        self.adress = dict()
        for line in self.file :
            if line == "\n" :
                continue
            a = line.split(' ')
            ip = a[0].split('.')
            ipint = []
            for ipintt in ip :
                ipint.append(int(ipintt))
            b = a[1].replace('\n','')
            self.adress[b] = ipint

    def printall(self):
        for item in self.adress :
            print(item , self.adress[item])

def IDClear (IDclock,ID):
    recoder = []
    while 1:
        IDclock.acquire()
        a =  time.time()
        #print("Getclock")
        for kv in ID:
            if time.time() - ID[kv][1] > 10 :
                recoder.append(kv)
        for i in recoder :
            #print("haha")
            ID.pop(i)
        recoder.clear()
        IDclock.release()
        #print("ReaseClock")
        #print("TIme" + str(time.time()-a))
        time.sleep(10)