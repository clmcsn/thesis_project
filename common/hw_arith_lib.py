
import common.verilog_template as vt

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

    #def writeCsaTree_sv(self):
