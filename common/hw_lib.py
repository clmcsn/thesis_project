import common.verilog_template as vt
import common.settings as s
from operator import xor
import os

def twos_comp(value, bits):
    if (value & (1<<(bits-1))) != 0:
        value=value - (1<<bits)
    return value

def FH(A,B,C):
    propagate=xor(A,B)
    sum=xor(propagate,C)
    carry=((A and B) or (C and propagate))
    res=str(sum)+str(carry)
    return res

def printer_2s(value,bits):
    if value>=0:
        sign_flag=True
        string=format(value,'b')
    else:
        sign_flag=False
        temp=format(value,'b')
        i=len(temp)-1
        inv=""
        while i>0:
            if (temp[i]=='1'):
                inv='0'+inv
            else:
                inv='1'+inv
            i-=1
        if len(inv)<bits:
            inv='1'+inv
        out=FH(int(inv[len(inv)-1]),0,1)
        string=""
        string=out[0]+string
        for bit in range(len(inv)-2,0,-1):
            out=FH(int(inv[bit]),0,int(out[1]))
            string=out[0]+string
        if out[1]=='1':
            string=out[1]+string
    while len(string)<bits:
        if sign_flag:
            string='0'+string
        else:
            string='1'+string
    return string

def integerTo2sFileConverter(infile,outfile,outpar):
    with open(infile,"r") as fin_pointer, open(outfile,"w") as fout_pointer:
        for line in fin_pointer:
            fout_pointer.write(printer_2s(int(line),outpar)+'\n')

"""Multiplier class for multiplication architecture analysis"""

class multiplier:
    #defines parallelism
    def __init__(self, parallelism):
        self.parallelism = parallelism
        self.weightValidationBits = "1"*parallelism #set by default all valid
        self.structure =[]
        self.pp_indexes=[0]*parallelism
        self.sum_inIndex=[0]*parallelism
        self.carry_inIndex=[0]*parallelism
        self.prod_index=0
        self.fh_count=0


    def setWeightValBits(self, newValidationBits):
        if (len(newValidationBits)!=self.parallelism):
            print("Validation Bits of partial products not congruent with parallelism")
            exit()
        else:
            self.weightValidationBits = newValidationBits[::-1]

    def genCsaStructure(self):
        for i in range(self.parallelism):
            if(self.weightValidationBits[i]=="1"):
                self.structure+=["p{}".format(i)]

    def printCsaStructure(self):
        for i in range(len(self.structure)):
            print(self.structure[i])

    def newCsaRow(self,tag,start,lenght):
        if ((start+lenght)>self.parallelism*2):
            print("Csa chain too long. Please check your design tag:{} start:{} lenght:{}".format(tag,start,lenght))
            exit()
        row=["0"]*(self.parallelism*2)
        for j in range(lenght):
            row[j+start]=tag
        return row

    def colBufferState(self,buffer,pos):
        if (buffer[0][pos]!="0" and buffer[1][pos]=="0" and buffer[2][pos]=="0"):
            return(0) #case we need to connect to final product
        elif (buffer[0][pos]=="0" and buffer[1][pos]=="0" and buffer[2][pos]=="0"):
            return(1) # we don't have to do nothing
        else:
            return(2) #allocate FH

    def chooseDataBit(self,tag):
        if (tag!="0"):
            row=int(tag[1])
        if (tag[0]=="p"):
            self.pp_indexes[row]+=1
            return vt.pps_bit.format(row,self.pp_indexes[row]-1)
        elif (tag[0]=="s"):
            self.sum_inIndex[row]+=1
            return vt.sums_bit.format(row,self.sum_inIndex[row]-1)
        elif (tag[0]=="c"):
            self.carry_inIndex[row]+=1
            return vt.carrys_bit.format(row,self.carry_inIndex[row]-1)
        else:
            return "1'b0"

    def elaborateBuffer(self,buffer,fout_pointer,level):
        firstCSA=True
        sumCoordinates=[0,0]
        for i in range(len(buffer[0])):
            case=self.colBufferState(buffer,i)
            if (case==0):
                fout_pointer.write(vt.assign_template.format(vt.product_bit.format(self.prod_index),self.chooseDataBit(buffer[0][i])))
                self.prod_index+=1
            elif (case==2):
                if (firstCSA):
                    sumCoordinates[0]=i
                    firstCSA=False
                fout_pointer.write(vt.FH_template.format(   self.fh_count,
                                                            self.chooseDataBit(buffer[0][i]),
                                                            self.chooseDataBit(buffer[1][i]),
                                                            self.chooseDataBit(buffer[2][i]),
                                                            vt.sums_bit.format(level,sumCoordinates[1]),
                                                            vt.carrys_bit.format(level,sumCoordinates[1])))
                sumCoordinates[1]+=1
                self.fh_count+=1
        return sumCoordinates

    def printBuffer(self,buffer):
        for i in range(len(buffer)):
            row=""
            for j in range(len(buffer[0])):
                if buffer[i][j]=="0":
                    row+=" 00"
                else:
                    row+=buffer[i][j]
                    row+=" "
            print(row+"\n")

    def writeCsaTree_sv(self):
        if (len(self.structure)<3):
            print("It's not possible to null more then {} bits".format(self.parallelism-3))
            exit()
        buffer=[] #used for recording buffer of data
        trace=self.structure #coping structure for poping up stages
        #init elaboration array buffer with first 3 partial products
        for i in range(3):
            row = self.newCsaRow(trace[0],int(trace[0][1]),self.parallelism)
            buffer.append(row)
            trace.pop(0)
        #assign 0s to LSB in case we don't have
        with open(s.csa_outPath,"w") as fout_pointer:
            i=0
            while(self.colBufferState(buffer,i)==1):
                i+=1
                fout_pointer.write(vt.assign_template.format(vt.product_bit.format(self.prod_index),"1'b0"))
                self.prod_index+=1
            for i in range(len(trace)):
                sum_indexes=self.elaborateBuffer(buffer,fout_pointer,i)
                buffer[0]=self.newCsaRow("s{}".format(i),sum_indexes[0],sum_indexes[1])
                buffer[1]=self.newCsaRow("c{}".format(i),sum_indexes[0]+1,sum_indexes[1])
                buffer[2]=self.newCsaRow(trace[i],int(trace[i][1]),self.parallelism)
            #last elaboration:
            sum_indexes=self.elaborateBuffer(buffer,fout_pointer,len(trace))
            buffer[0]=self.newCsaRow("s{}".format(i+1),sum_indexes[0],sum_indexes[1])
            buffer[1]=self.newCsaRow("c{}".format(i+1),sum_indexes[0]+1,sum_indexes[1])
            #write last product assignment
            fout_pointer.write(vt.assign_template.format(vt.product_bit.format(self.prod_index),self.chooseDataBit("s{}".format(i+1))))
            self.prod_index+=1
            #write adder
            fout_pointer.write(vt.RCA_template.format(      sum_indexes[1],
                                                            1,
                                                            "{1'b0,"+vt.sums_bus.format(i+1,sum_indexes[1]-1,1)+"}",
                                                            vt.carrys_bus.format(i+1,sum_indexes[1]-1,0),
                                                            "1'b0",
                                                            vt.product_bus.format(sum_indexes[1]+self.prod_index-1,self.prod_index)))
            self.prod_index+=sum_indexes[1]
            #case in which last bit is 0
            while(self.prod_index<2*self.parallelism):
                fout_pointer.write(vt.assign_template.format(vt.product_bit.format(self.prod_index),"1'b0"))
                self.prod_index+=1
    #generates and put the multiplier in the component directory
    def genCsaMultiplier(self):
        fileName="multiplier.sv"
        self.writeCsaTree_sv()
        with open(fileName,"w") as fout_pointer, open(s.templatePath+fileName,"r") as fin_pointer, open(s.csa_outPath,"r") as auto_pointer:
            line=fin_pointer.readline()
            while (not(s.signal_string in line)):
                fout_pointer.write(line)
                line=fin_pointer.readline()
            for line in auto_pointer:
                fout_pointer.write(line)
            for line in fin_pointer:
                fout_pointer.write(line)
        os.remove(s.csa_outPath)
        try:
            os.remove(s.componentsPath+fileName)
        except:
            pass
        os.rename(fileName,s.componentsPath+fileName)
