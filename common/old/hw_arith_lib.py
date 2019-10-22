
import common.verilog_template as vt
import common.settings as s
"""Multiplier class for multiplication architecture analysis"""

class multiplier:
    #defines parallelism
    def __init__(self, parallelism):
        self.parallelism = parallelism
        self.weightValidationBits = "1"*parallelism
        self.structure =[]

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

    def genTreeStructure(self):
        for i in range(self.parallelism):
            row=[]
            row+=[["0"]]*(2*self.parallelism-1)
            if (self.weightValidationBits[i]=="1"):
                for j in range(self.parallelism):
                    row[j+i]=["p{}".format(i)]
            self.structure.append(row)

    def printCsaStructure(self):
        for i in range(len(self.structure)):
            print(self.structure[i])

    def printTreeStructure(self):
        for i in range(self.parallelism):
            row=""
            for j in range(self.parallelism*2-1):
                row+=str(self.structure[i][j])
            print(row)

    def bubbleSort(self):
        for i in range(self.parallelism*2-1):
            col=[]
            for j in range(self.parallelism):
                if (self.structure[j][i]!=["0"]):
                    col+=[self.structure[j][i]]
            col+=[["0"]]*(self.parallelism-len(col))
            for j in range(self.parallelism):
                self.structure[j][i]=col[j]

    def newRow(self,trace,start):
        row=["0"]*(self.parallelism*2-1)
        for j in range(self.parallelism):
            row[j+start]=trace
        return row

    def whichCase(self,buffer,pos):
        if (buffer[0][pos]!="0" and buffer[1][pos]=="0" and buffer[2][pos]=="0"):
            return(0) #case we need to connect to final product
        elif (buffer[0][pos]=="0" and buffer[1][pos]=="0" and buffer[2][pos]=="0"):
            return(1) # we don't have to do nothing
        else:
            return(2) #allocate FH

    def chooseDataBit(self,tag,pp,sum,carry):
        if (tag[0]=="p"):
            pp+=1
            return vt.pps_bit.format(int(tag[1]),pp-1)
        elif (tag[0]=="s"):
            sum+=1
            return vt.sums_bit.format(int(tag[1]),sum-1)
        elif (tag[0]=="c"):
            carry+=1
            return vt.carrys_bit.format(int(tag[1]),carry-1)
        else:
            return "1'b0"

    def elaborateBuffer(self,buffer,fout_pointer,prod_index,level,fh_count):
        firstCSA=True
        outSumIndex=0
        for i in range(len(buffer[0])):
            pp_i=0
            in_sum_i=0
            in_carry_i=0
            out_i=0
            case=self.whichCase(buffer,i)
            if (case==0):
                fout_pointer.write(vt.assign_template.format(vt.product_bit.format(prod_index),self.chooseDataBit(buffer[0][i],pp_i,in_sum_i,in_carry_i)))
                prod_index+=1
            elif (case==2):
                if (firstCSA):
                    outSumIndex=i
                    firstCSA=False
                fout_pointer.write(vt.FH_template.format(   fh_count,
                                                            self.chooseDataBit(buffer[0][i],pp_i,in_sum_i,in_carry_i),
                                                            self.chooseDataBit(buffer[1][i],pp_i,in_sum_i,in_carry_i),
                                                            self.chooseDataBit(buffer[2][i],pp_i,in_sum_i,in_carry_i),
                                                            vt.sums_bit.format(level,out_i),
                                                            vt.carrys_bit.format(level,out_i)))
                out_i+=1
                fh_count+=1
        return outSumIndex

    def writeCsaTree_sv(self):
        if (len(self.structure)<3):
            print("It's not possible to null more then {} bits".format(self.parallelism-3))
            exit()
        new_buffer=[] #used for recording next stage buffer of data
        pres_buffer=[] #used for elaborating actual buffer
        trace=self.structure #coping structure for poping up stages
        #init elaboration array (pres_buffer) with first 3 partial products
        for i in range(3):
            row = self.newRow(trace[0],int(trace[0][1]))
            pres_buffer.append(row)
            trace.pop(0)
        #assign 0s to LSB in case we don't have
        i=0
        fh_i=0
        with open(s.csa_outPath,"w") as fout_pointer:
            prod_index=0
            while(self.whichCase(pres_buffer,i)==2):
                fout_pointer.write(vt.assign_template.format(product_bit.format(prod_index),"1'b0"))
                i+=1
                prod_index+=1
            for i in range(len(trace)):
                sum_index=self.elaborateBuffer(pres_buffer,fout_pointer,prod_index,i,fh_i)
                pres_buffer[0]=self.newRow("s{}".format(i),sum_index)
                pres_buffer[1]=self.newRow("c{}".format(i),sum_index+1)
                pres_buffer[2]=self.newRow(trace[0],int(trace[0][1]))
        #write fullAdder (we need to check prod indexes!)
