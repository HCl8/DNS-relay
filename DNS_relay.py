from DNS_struct import *
from socket import *
import random
import threading
import _thread
import time
import json
import argparse

settings=json.load(open("settings.json","r"))
DEBUG=settings['DEBUG']
DNSRELAY_FILE=settings['DNSRELAY_FILE']
SUPER_DNS=settings["SUPER_DNS"]

parse=argparse.ArgumentParser()
parse.add_argument('-dl','--dlevel',required=False,type=int,help='0/1/2 degree of debug')
parse.add_argument('-f','--file',required=False,type=str,help='location of DNS_relay.txt')
parse.add_argument('-i','--ip',required=False,type=str,help='set DNS ip')
args=parse.parse_args()
print(args)
if args.dlevel:
    DEBUG=args.dlevel
if args.file:
    DNSRELAY_FILE=args.file
if args.ip:
    SUPER_DNS=args.ip
#建立套接字 监听接口
DNS = socket(AF_INET,SOCK_DGRAM)
adress = ('',53)
DNS.bind(adress)
ip = AdressList(DNSRELAY_FILE) #读入ip - 域名对照表
super_dns = (SUPER_DNS,53) #设置上层DNS服务器
ID = dict()

IDclock = threading.Lock()
_thread.start_new_thread(IDClear,(IDclock,ID))

def debug(*a,level = 1,end="\n"):
    if level<=DEBUG:
        for i in a:
            print(i,end="")
        print(end,end="")

debug("DEBUG    ",DEBUG)
debug("DNSRELAY_FILE    ",DNSRELAY_FILE)
debug("SUPER_DNS    ",SUPER_DNS)

def qq(data): 
    qa = DnsAnalysis(data[0])
    #debug("len :" + str(len(data[0])))
    #debug("ID: " + str(qa.ID()))
    #qa.printall()
    debug("ADRESS: " + qa.QNAME())
    debug(qa.Debug(),level=2)
    debug(qa.printall(),level=2)


    if qa.QR() == 1 : #如果是应答报文 转发
        if qa.ID() in ID :  #有ID记录的转发 否则丢掉
            tempadress = ID[qa.ID()][0]
            if len(tempadress[0]) == 2 :  #ID是重复然后被修改的情况 ID修改为原ID
                Message = DnsCreate(data[0])
                Message.setID(tempadress[1])
                i = DNS.sendto(Message.GetBytes(),tempadress[0])
                debug("ChangeID send to" + str(tempadress[0])+ str(i),2) + str(qa.ID()) + "->" +str(tempadress[1])
                #debug("ID ++" + str(tempadress[1]) , 2)
            else : #正常转发
                i = DNS.sendto(data[0],tempadress)
                debug("Normal send to" + str(tempadress)+ str(i))
            # try:
            #     ID.pop(qa.ID())
            # except:
            #     pass
            ID.pop(qa.ID())
    else : #处理请求报文
        if qa.QNAME() in ip.adress and qa.QTYPE() == 1: #如果是ipv4请求且地址在IP对照表里
            adresstemp = ip.adress[qa.QNAME()]
            Message = DnsCreate(data[0])
            if adresstemp == [0,0,0,0] : # 如果地址是0.0.0.0 则rcode设置为3
                Message.setRCODE(3)
            else :  #否则 生成回复报文 然后发送
                Message.setQR(1)
                Message.setRDATA(adresstemp)
            i = DNS.sendto(Message.GetBytes(), data[1])
            debug("In IP-List send to" + str(data[1])+ str(i))
        else:
            if qa.ID() in ID : #如果ID冲突　随机生成一个新ID 将新ID 原ID ip 记住
                if data[1] == ID[qa.ID()][0] :
                    debug("ID—IP重复 丢弃")
                    return
                tempID = random.randint(0,65535)
                while tempID in ID :
                    tempID = random.randint(0,65535)
                Message = DnsCreate(data[0])
                Message.setID(tempID)
                ID[tempID] = ((data[1],qa.ID()),time.time())
                i = DNS.sendto(Message.GetBytes(),super_dns)
                debug("ChangeID to SDNS :" + str(super_dns) + str(i))+ str(qa.ID()) + "->" + str(tempID)
            else :  # 将ID - ip 记录 然后转发
                ID[qa.ID()] = (data[1],time.time())
                i = DNS.sendto(data[0], super_dns)
                debug("Normal send to SDNS :" + str(super_dns)+ str(i))

def main():
    while 1 :
        # noinspection PyBroadException
        try:
            data = DNS.recvfrom(1024)
            # data,address=DNS.recvfrom(1024)
        except :
            debug("exception Maybe 10054")
            continue
        debug()
        debug("From:   " + str(data[1]))
        # a=threading.Thread(target=qq,args=(data,))
        # a.start()
        IDclock.acquire()
        qq(data)
        IDclock.release()
        #DNS.close()
        #DNS = socket(AF_INET, SOCK_DGRAM)
        #adress = ('0.0.0.0', 53)
        #DNS.bind(adress)

        #调试信息
        #debug()
        #debug()


if __name__ =='__main__':
    main()