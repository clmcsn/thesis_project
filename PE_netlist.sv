/////////////////////////////////////////////////////////////
// Created by: Synopsys DC Expert(TM) in wire load mode
// Version   : M-2016.12
// Date      : Thu Oct 17 15:07:48 2019
/////////////////////////////////////////////////////////////


module PE ( activation, weight, inPartialSum, outPartialSum, clk, rst_n );
  input [7:0] activation;
  input [7:0] weight;
  input [31:0] inPartialSum;
  output [31:0] outPartialSum;
  input clk, rst_n;
  wire   activationRegister_n2, activationRegister_n1, activationRegister_n10,
         activationRegister_n9, activationRegister_n8, activationRegister_n7,
         activationRegister_n6, activationRegister_n5, activationRegister_n4,
         activationRegister_n3, weightRegister_n18, weightRegister_n17,
         weightRegister_n16, weightRegister_n15, weightRegister_n14,
         weightRegister_n13, weightRegister_n12, weightRegister_n11,
         weightRegister_n2, weightRegister_n1, partialSumRegister_n2,
         partialSumRegister_n1, partialSumRegister_n34, partialSumRegister_n33,
         partialSumRegister_n32, partialSumRegister_n31,
         partialSumRegister_n30, partialSumRegister_n29,
         partialSumRegister_n28, partialSumRegister_n27,
         partialSumRegister_n26, partialSumRegister_n25,
         partialSumRegister_n24, partialSumRegister_n23,
         partialSumRegister_n22, partialSumRegister_n21,
         partialSumRegister_n20, partialSumRegister_n19,
         partialSumRegister_n18, partialSumRegister_n17,
         partialSumRegister_n16, partialSumRegister_n15,
         partialSumRegister_n14, partialSumRegister_n13,
         partialSumRegister_n12, partialSumRegister_n11,
         partialSumRegister_n10, partialSumRegister_n9, partialSumRegister_n8,
         partialSumRegister_n7, partialSumRegister_n6, partialSumRegister_n5,
         partialSumRegister_n4, partialSumRegister_n3, mult_mult_12_n23,
         mult_mult_12_n22, mult_mult_12_n21, mult_mult_12_n20,
         mult_mult_12_n19, mult_mult_12_n18, mult_mult_12_n17,
         mult_mult_12_n16, mult_mult_12_n15, mult_mult_12_n14,
         mult_mult_12_n13, mult_mult_12_n12, mult_mult_12_n11,
         mult_mult_12_n10, mult_mult_12_n9, mult_mult_12_n8, mult_mult_12_n7,
         mult_mult_12_n6, mult_mult_12_n5, mult_mult_12_n4, mult_mult_12_n3,
         mult_mult_12_SUMB_1__1_, mult_mult_12_SUMB_1__2_,
         mult_mult_12_SUMB_1__3_, mult_mult_12_SUMB_1__4_,
         mult_mult_12_SUMB_1__5_, mult_mult_12_SUMB_1__6_,
         mult_mult_12_SUMB_2__1_, mult_mult_12_SUMB_2__2_,
         mult_mult_12_SUMB_2__3_, mult_mult_12_SUMB_2__4_,
         mult_mult_12_SUMB_2__5_, mult_mult_12_SUMB_3__1_,
         mult_mult_12_SUMB_3__2_, mult_mult_12_SUMB_3__3_,
         mult_mult_12_SUMB_3__4_, mult_mult_12_SUMB_4__1_,
         mult_mult_12_SUMB_4__2_, mult_mult_12_SUMB_4__3_,
         mult_mult_12_SUMB_5__1_, mult_mult_12_SUMB_5__2_,
         mult_mult_12_SUMB_6__1_, mult_mult_12_CARRYB_2__0_,
         mult_mult_12_CARRYB_2__1_, mult_mult_12_CARRYB_2__2_,
         mult_mult_12_CARRYB_2__3_, mult_mult_12_CARRYB_2__4_,
         mult_mult_12_CARRYB_3__0_, mult_mult_12_CARRYB_3__1_,
         mult_mult_12_CARRYB_3__2_, mult_mult_12_CARRYB_3__3_,
         mult_mult_12_CARRYB_4__0_, mult_mult_12_CARRYB_4__1_,
         mult_mult_12_CARRYB_4__2_, mult_mult_12_CARRYB_5__0_,
         mult_mult_12_CARRYB_5__1_, mult_mult_12_CARRYB_6__0_,
         mult_mult_12_ab_0__1_, mult_mult_12_ab_0__2_, mult_mult_12_ab_0__3_,
         mult_mult_12_ab_0__4_, mult_mult_12_ab_0__5_, mult_mult_12_ab_0__6_,
         mult_mult_12_ab_0__7_, mult_mult_12_ab_1__0_, mult_mult_12_ab_1__1_,
         mult_mult_12_ab_1__2_, mult_mult_12_ab_1__3_, mult_mult_12_ab_1__4_,
         mult_mult_12_ab_1__5_, mult_mult_12_ab_1__6_, mult_mult_12_ab_2__0_,
         mult_mult_12_ab_2__1_, mult_mult_12_ab_2__2_, mult_mult_12_ab_2__3_,
         mult_mult_12_ab_2__4_, mult_mult_12_ab_2__5_, mult_mult_12_ab_3__0_,
         mult_mult_12_ab_3__1_, mult_mult_12_ab_3__2_, mult_mult_12_ab_3__3_,
         mult_mult_12_ab_3__4_, mult_mult_12_ab_4__0_, mult_mult_12_ab_4__1_,
         mult_mult_12_ab_4__2_, mult_mult_12_ab_4__3_, mult_mult_12_ab_5__0_,
         mult_mult_12_ab_5__1_, mult_mult_12_ab_5__2_, mult_mult_12_ab_6__0_,
         mult_mult_12_ab_6__1_, mult_mult_12_ab_7__0_;
  wire   [7:0] activationToMult;
  wire   [7:0] weightToMult;
  wire   [31:0] pSumToAdd;
  wire   [15:0] prodToAdd;
  wire   [31:1] add_r67_carry;

  NR2M1R activationRegister_U11 ( .A(1'b1), .B(1'b0), .Z(activationRegister_n1) );
  NR2M1R activationRegister_U10 ( .A(activationRegister_n1), .B(1'b0), .Z(
        activationRegister_n2) );
  AO22M1RA activationRegister_U9 ( .A1(activationToMult[7]), .A2(
        activationRegister_n1), .B1(activation[7]), .B2(activationRegister_n2), 
        .Z(activationRegister_n10) );
  AO22M1RA activationRegister_U8 ( .A1(activationToMult[0]), .A2(
        activationRegister_n1), .B1(activation[0]), .B2(activationRegister_n2), 
        .Z(activationRegister_n3) );
  AO22M1RA activationRegister_U7 ( .A1(activationToMult[1]), .A2(
        activationRegister_n1), .B1(activation[1]), .B2(activationRegister_n2), 
        .Z(activationRegister_n4) );
  AO22M1RA activationRegister_U6 ( .A1(activationToMult[2]), .A2(
        activationRegister_n1), .B1(activation[2]), .B2(activationRegister_n2), 
        .Z(activationRegister_n5) );
  AO22M1RA activationRegister_U5 ( .A1(activationToMult[3]), .A2(
        activationRegister_n1), .B1(activation[3]), .B2(activationRegister_n2), 
        .Z(activationRegister_n6) );
  AO22M1RA activationRegister_U4 ( .A1(activationToMult[4]), .A2(
        activationRegister_n1), .B1(activation[4]), .B2(activationRegister_n2), 
        .Z(activationRegister_n7) );
  AO22M1RA activationRegister_U3 ( .A1(activationToMult[5]), .A2(
        activationRegister_n1), .B1(activation[5]), .B2(activationRegister_n2), 
        .Z(activationRegister_n8) );
  AO22M1RA activationRegister_U2 ( .A1(activationToMult[6]), .A2(
        activationRegister_n1), .B1(activation[6]), .B2(activationRegister_n2), 
        .Z(activationRegister_n9) );
  DFQRM2RA activationRegister_temp_reg_0_ ( .D(activationRegister_n3), .CK(clk), .RB(rst_n), .Q(activationToMult[0]) );
  DFQRM2RA activationRegister_temp_reg_1_ ( .D(activationRegister_n4), .CK(clk), .RB(rst_n), .Q(activationToMult[1]) );
  DFQRM2RA activationRegister_temp_reg_2_ ( .D(activationRegister_n5), .CK(clk), .RB(rst_n), .Q(activationToMult[2]) );
  DFQRM2RA activationRegister_temp_reg_3_ ( .D(activationRegister_n6), .CK(clk), .RB(rst_n), .Q(activationToMult[3]) );
  DFQRM2RA activationRegister_temp_reg_4_ ( .D(activationRegister_n7), .CK(clk), .RB(rst_n), .Q(activationToMult[4]) );
  DFQRM2RA activationRegister_temp_reg_5_ ( .D(activationRegister_n8), .CK(clk), .RB(rst_n), .Q(activationToMult[5]) );
  DFQRM2RA activationRegister_temp_reg_6_ ( .D(activationRegister_n9), .CK(clk), .RB(rst_n), .Q(activationToMult[6]) );
  DFQRM2RA activationRegister_temp_reg_7_ ( .D(activationRegister_n10), .CK(
        clk), .RB(rst_n), .Q(activationToMult[7]) );
  NR2M1R weightRegister_U11 ( .A(1'b1), .B(1'b0), .Z(weightRegister_n1) );
  NR2M1R weightRegister_U10 ( .A(weightRegister_n1), .B(1'b0), .Z(
        weightRegister_n2) );
  AO22M1RA weightRegister_U9 ( .A1(weightToMult[7]), .A2(weightRegister_n1), 
        .B1(weight[7]), .B2(weightRegister_n2), .Z(weightRegister_n11) );
  AO22M1RA weightRegister_U8 ( .A1(weightToMult[0]), .A2(weightRegister_n1), 
        .B1(weight[0]), .B2(weightRegister_n2), .Z(weightRegister_n18) );
  AO22M1RA weightRegister_U7 ( .A1(weightToMult[1]), .A2(weightRegister_n1), 
        .B1(weight[1]), .B2(weightRegister_n2), .Z(weightRegister_n17) );
  AO22M1RA weightRegister_U6 ( .A1(weightToMult[2]), .A2(weightRegister_n1), 
        .B1(weight[2]), .B2(weightRegister_n2), .Z(weightRegister_n16) );
  AO22M1RA weightRegister_U5 ( .A1(weightToMult[3]), .A2(weightRegister_n1), 
        .B1(weight[3]), .B2(weightRegister_n2), .Z(weightRegister_n15) );
  AO22M1RA weightRegister_U4 ( .A1(weightToMult[4]), .A2(weightRegister_n1), 
        .B1(weight[4]), .B2(weightRegister_n2), .Z(weightRegister_n14) );
  AO22M1RA weightRegister_U3 ( .A1(weightToMult[5]), .A2(weightRegister_n1), 
        .B1(weight[5]), .B2(weightRegister_n2), .Z(weightRegister_n13) );
  AO22M1RA weightRegister_U2 ( .A1(weightToMult[6]), .A2(weightRegister_n1), 
        .B1(weight[6]), .B2(weightRegister_n2), .Z(weightRegister_n12) );
  DFQRM2RA weightRegister_temp_reg_0_ ( .D(weightRegister_n18), .CK(clk), .RB(
        rst_n), .Q(weightToMult[0]) );
  DFQRM2RA weightRegister_temp_reg_1_ ( .D(weightRegister_n17), .CK(clk), .RB(
        rst_n), .Q(weightToMult[1]) );
  DFQRM2RA weightRegister_temp_reg_2_ ( .D(weightRegister_n16), .CK(clk), .RB(
        rst_n), .Q(weightToMult[2]) );
  DFQRM2RA weightRegister_temp_reg_3_ ( .D(weightRegister_n15), .CK(clk), .RB(
        rst_n), .Q(weightToMult[3]) );
  DFQRM2RA weightRegister_temp_reg_4_ ( .D(weightRegister_n14), .CK(clk), .RB(
        rst_n), .Q(weightToMult[4]) );
  DFQRM2RA weightRegister_temp_reg_5_ ( .D(weightRegister_n13), .CK(clk), .RB(
        rst_n), .Q(weightToMult[5]) );
  DFQRM2RA weightRegister_temp_reg_6_ ( .D(weightRegister_n12), .CK(clk), .RB(
        rst_n), .Q(weightToMult[6]) );
  DFQRM2RA weightRegister_temp_reg_7_ ( .D(weightRegister_n11), .CK(clk), .RB(
        rst_n), .Q(weightToMult[7]) );
  AO22M1RA partialSumRegister_U35 ( .A1(pSumToAdd[7]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[7]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n10) );
  AO22M1RA partialSumRegister_U34 ( .A1(pSumToAdd[8]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[8]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n11) );
  AO22M1RA partialSumRegister_U33 ( .A1(pSumToAdd[9]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[9]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n12) );
  AO22M1RA partialSumRegister_U32 ( .A1(pSumToAdd[10]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[10]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n13) );
  AO22M1RA partialSumRegister_U31 ( .A1(pSumToAdd[11]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[11]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n14) );
  AO22M1RA partialSumRegister_U30 ( .A1(pSumToAdd[12]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[12]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n15) );
  AO22M1RA partialSumRegister_U29 ( .A1(pSumToAdd[13]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[13]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n16) );
  AO22M1RA partialSumRegister_U28 ( .A1(pSumToAdd[14]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[14]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n17) );
  AO22M1RA partialSumRegister_U27 ( .A1(pSumToAdd[15]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[15]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n18) );
  AO22M1RA partialSumRegister_U26 ( .A1(pSumToAdd[16]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[16]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n19) );
  AO22M1RA partialSumRegister_U25 ( .A1(pSumToAdd[17]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[17]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n20) );
  AO22M1RA partialSumRegister_U24 ( .A1(pSumToAdd[18]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[18]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n21) );
  AO22M1RA partialSumRegister_U23 ( .A1(pSumToAdd[19]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[19]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n22) );
  AO22M1RA partialSumRegister_U22 ( .A1(pSumToAdd[20]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[20]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n23) );
  AO22M1RA partialSumRegister_U21 ( .A1(pSumToAdd[21]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[21]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n24) );
  AO22M1RA partialSumRegister_U20 ( .A1(pSumToAdd[22]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[22]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n25) );
  AO22M1RA partialSumRegister_U19 ( .A1(pSumToAdd[23]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[23]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n26) );
  AO22M1RA partialSumRegister_U18 ( .A1(pSumToAdd[24]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[24]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n27) );
  AO22M1RA partialSumRegister_U17 ( .A1(pSumToAdd[25]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[25]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n28) );
  AO22M1RA partialSumRegister_U16 ( .A1(pSumToAdd[26]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[26]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n29) );
  AO22M1RA partialSumRegister_U15 ( .A1(pSumToAdd[0]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[0]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n3) );
  AO22M1RA partialSumRegister_U14 ( .A1(pSumToAdd[27]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[27]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n30) );
  AO22M1RA partialSumRegister_U13 ( .A1(pSumToAdd[28]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[28]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n31) );
  AO22M1RA partialSumRegister_U12 ( .A1(pSumToAdd[29]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[29]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n32) );
  AO22M1RA partialSumRegister_U11 ( .A1(pSumToAdd[30]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[30]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n33) );
  AO22M1RA partialSumRegister_U10 ( .A1(pSumToAdd[31]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[31]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n34) );
  AO22M1RA partialSumRegister_U9 ( .A1(pSumToAdd[1]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[1]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n4) );
  AO22M1RA partialSumRegister_U8 ( .A1(pSumToAdd[2]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[2]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n5) );
  AO22M1RA partialSumRegister_U7 ( .A1(pSumToAdd[3]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[3]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n6) );
  AO22M1RA partialSumRegister_U6 ( .A1(pSumToAdd[4]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[4]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n7) );
  AO22M1RA partialSumRegister_U5 ( .A1(pSumToAdd[5]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[5]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n8) );
  AO22M1RA partialSumRegister_U4 ( .A1(pSumToAdd[6]), .A2(
        partialSumRegister_n1), .B1(inPartialSum[6]), .B2(
        partialSumRegister_n2), .Z(partialSumRegister_n9) );
  NR2M2R partialSumRegister_U3 ( .A(partialSumRegister_n1), .B(1'b0), .Z(
        partialSumRegister_n2) );
  NR2M2R partialSumRegister_U2 ( .A(1'b1), .B(1'b0), .Z(partialSumRegister_n1)
         );
  DFQRM2RA partialSumRegister_temp_reg_0_ ( .D(partialSumRegister_n3), .CK(clk), .RB(rst_n), .Q(pSumToAdd[0]) );
  DFQRM2RA partialSumRegister_temp_reg_1_ ( .D(partialSumRegister_n4), .CK(clk), .RB(rst_n), .Q(pSumToAdd[1]) );
  DFQRM2RA partialSumRegister_temp_reg_2_ ( .D(partialSumRegister_n5), .CK(clk), .RB(rst_n), .Q(pSumToAdd[2]) );
  DFQRM2RA partialSumRegister_temp_reg_3_ ( .D(partialSumRegister_n6), .CK(clk), .RB(rst_n), .Q(pSumToAdd[3]) );
  DFQRM2RA partialSumRegister_temp_reg_4_ ( .D(partialSumRegister_n7), .CK(clk), .RB(rst_n), .Q(pSumToAdd[4]) );
  DFQRM2RA partialSumRegister_temp_reg_5_ ( .D(partialSumRegister_n8), .CK(clk), .RB(rst_n), .Q(pSumToAdd[5]) );
  DFQRM2RA partialSumRegister_temp_reg_6_ ( .D(partialSumRegister_n9), .CK(clk), .RB(rst_n), .Q(pSumToAdd[6]) );
  DFQRM2RA partialSumRegister_temp_reg_7_ ( .D(partialSumRegister_n10), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[7]) );
  DFQRM2RA partialSumRegister_temp_reg_8_ ( .D(partialSumRegister_n11), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[8]) );
  DFQRM2RA partialSumRegister_temp_reg_9_ ( .D(partialSumRegister_n12), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[9]) );
  DFQRM2RA partialSumRegister_temp_reg_10_ ( .D(partialSumRegister_n13), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[10]) );
  DFQRM2RA partialSumRegister_temp_reg_11_ ( .D(partialSumRegister_n14), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[11]) );
  DFQRM2RA partialSumRegister_temp_reg_12_ ( .D(partialSumRegister_n15), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[12]) );
  DFQRM2RA partialSumRegister_temp_reg_13_ ( .D(partialSumRegister_n16), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[13]) );
  DFQRM2RA partialSumRegister_temp_reg_14_ ( .D(partialSumRegister_n17), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[14]) );
  DFQRM2RA partialSumRegister_temp_reg_15_ ( .D(partialSumRegister_n18), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[15]) );
  DFQRM2RA partialSumRegister_temp_reg_16_ ( .D(partialSumRegister_n19), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[16]) );
  DFQRM2RA partialSumRegister_temp_reg_17_ ( .D(partialSumRegister_n20), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[17]) );
  DFQRM2RA partialSumRegister_temp_reg_18_ ( .D(partialSumRegister_n21), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[18]) );
  DFQRM2RA partialSumRegister_temp_reg_19_ ( .D(partialSumRegister_n22), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[19]) );
  DFQRM2RA partialSumRegister_temp_reg_20_ ( .D(partialSumRegister_n23), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[20]) );
  DFQRM2RA partialSumRegister_temp_reg_21_ ( .D(partialSumRegister_n24), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[21]) );
  DFQRM2RA partialSumRegister_temp_reg_22_ ( .D(partialSumRegister_n25), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[22]) );
  DFQRM2RA partialSumRegister_temp_reg_23_ ( .D(partialSumRegister_n26), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[23]) );
  DFQRM2RA partialSumRegister_temp_reg_24_ ( .D(partialSumRegister_n27), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[24]) );
  DFQRM2RA partialSumRegister_temp_reg_25_ ( .D(partialSumRegister_n28), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[25]) );
  DFQRM2RA partialSumRegister_temp_reg_26_ ( .D(partialSumRegister_n29), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[26]) );
  DFQRM2RA partialSumRegister_temp_reg_27_ ( .D(partialSumRegister_n30), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[27]) );
  DFQRM2RA partialSumRegister_temp_reg_28_ ( .D(partialSumRegister_n31), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[28]) );
  DFQRM2RA partialSumRegister_temp_reg_29_ ( .D(partialSumRegister_n32), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[29]) );
  DFQRM2RA partialSumRegister_temp_reg_30_ ( .D(partialSumRegister_n33), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[30]) );
  DFQRM2RA partialSumRegister_temp_reg_31_ ( .D(partialSumRegister_n34), .CK(
        clk), .RB(rst_n), .Q(pSumToAdd[31]) );
  NR2M1R mult_mult_12_U65 ( .A(mult_mult_12_n23), .B(mult_mult_12_n16), .Z(
        prodToAdd[0]) );
  NR2M1R mult_mult_12_U64 ( .A(mult_mult_12_n22), .B(mult_mult_12_n16), .Z(
        mult_mult_12_ab_0__1_) );
  NR2M1R mult_mult_12_U63 ( .A(mult_mult_12_n21), .B(mult_mult_12_n16), .Z(
        mult_mult_12_ab_0__2_) );
  NR2M1R mult_mult_12_U62 ( .A(mult_mult_12_n20), .B(mult_mult_12_n16), .Z(
        mult_mult_12_ab_0__3_) );
  NR2M1R mult_mult_12_U61 ( .A(mult_mult_12_n19), .B(mult_mult_12_n16), .Z(
        mult_mult_12_ab_0__4_) );
  NR2M1R mult_mult_12_U60 ( .A(mult_mult_12_n18), .B(mult_mult_12_n16), .Z(
        mult_mult_12_ab_0__5_) );
  NR2M1R mult_mult_12_U59 ( .A(mult_mult_12_n17), .B(mult_mult_12_n16), .Z(
        mult_mult_12_ab_0__6_) );
  NR2M1R mult_mult_12_U58 ( .A(mult_mult_12_n23), .B(mult_mult_12_n15), .Z(
        mult_mult_12_ab_1__0_) );
  NR2M1R mult_mult_12_U57 ( .A(mult_mult_12_n22), .B(mult_mult_12_n15), .Z(
        mult_mult_12_ab_1__1_) );
  NR2M1R mult_mult_12_U56 ( .A(mult_mult_12_n21), .B(mult_mult_12_n15), .Z(
        mult_mult_12_ab_1__2_) );
  NR2M1R mult_mult_12_U55 ( .A(mult_mult_12_n20), .B(mult_mult_12_n15), .Z(
        mult_mult_12_ab_1__3_) );
  NR2M1R mult_mult_12_U54 ( .A(mult_mult_12_n19), .B(mult_mult_12_n15), .Z(
        mult_mult_12_ab_1__4_) );
  NR2M1R mult_mult_12_U53 ( .A(mult_mult_12_n18), .B(mult_mult_12_n15), .Z(
        mult_mult_12_ab_1__5_) );
  NR2M1R mult_mult_12_U52 ( .A(mult_mult_12_n17), .B(mult_mult_12_n15), .Z(
        mult_mult_12_ab_1__6_) );
  NR2M1R mult_mult_12_U51 ( .A(mult_mult_12_n23), .B(mult_mult_12_n14), .Z(
        mult_mult_12_ab_2__0_) );
  NR2M1R mult_mult_12_U50 ( .A(mult_mult_12_n22), .B(mult_mult_12_n14), .Z(
        mult_mult_12_ab_2__1_) );
  NR2M1R mult_mult_12_U49 ( .A(mult_mult_12_n21), .B(mult_mult_12_n14), .Z(
        mult_mult_12_ab_2__2_) );
  NR2M1R mult_mult_12_U48 ( .A(mult_mult_12_n20), .B(mult_mult_12_n14), .Z(
        mult_mult_12_ab_2__3_) );
  NR2M1R mult_mult_12_U47 ( .A(mult_mult_12_n19), .B(mult_mult_12_n14), .Z(
        mult_mult_12_ab_2__4_) );
  NR2M1R mult_mult_12_U46 ( .A(mult_mult_12_n18), .B(mult_mult_12_n14), .Z(
        mult_mult_12_ab_2__5_) );
  NR2M1R mult_mult_12_U45 ( .A(mult_mult_12_n23), .B(mult_mult_12_n13), .Z(
        mult_mult_12_ab_3__0_) );
  NR2M1R mult_mult_12_U44 ( .A(mult_mult_12_n22), .B(mult_mult_12_n13), .Z(
        mult_mult_12_ab_3__1_) );
  NR2M1R mult_mult_12_U43 ( .A(mult_mult_12_n21), .B(mult_mult_12_n13), .Z(
        mult_mult_12_ab_3__2_) );
  NR2M1R mult_mult_12_U42 ( .A(mult_mult_12_n20), .B(mult_mult_12_n13), .Z(
        mult_mult_12_ab_3__3_) );
  NR2M1R mult_mult_12_U41 ( .A(mult_mult_12_n19), .B(mult_mult_12_n13), .Z(
        mult_mult_12_ab_3__4_) );
  NR2M1R mult_mult_12_U40 ( .A(mult_mult_12_n23), .B(mult_mult_12_n12), .Z(
        mult_mult_12_ab_4__0_) );
  NR2M1R mult_mult_12_U39 ( .A(mult_mult_12_n22), .B(mult_mult_12_n12), .Z(
        mult_mult_12_ab_4__1_) );
  NR2M1R mult_mult_12_U38 ( .A(mult_mult_12_n21), .B(mult_mult_12_n12), .Z(
        mult_mult_12_ab_4__2_) );
  NR2M1R mult_mult_12_U37 ( .A(mult_mult_12_n20), .B(mult_mult_12_n12), .Z(
        mult_mult_12_ab_4__3_) );
  NR2M1R mult_mult_12_U36 ( .A(mult_mult_12_n23), .B(mult_mult_12_n11), .Z(
        mult_mult_12_ab_5__0_) );
  NR2M1R mult_mult_12_U35 ( .A(mult_mult_12_n22), .B(mult_mult_12_n11), .Z(
        mult_mult_12_ab_5__1_) );
  NR2M1R mult_mult_12_U34 ( .A(mult_mult_12_n21), .B(mult_mult_12_n11), .Z(
        mult_mult_12_ab_5__2_) );
  NR2M1R mult_mult_12_U33 ( .A(mult_mult_12_n23), .B(mult_mult_12_n10), .Z(
        mult_mult_12_ab_6__0_) );
  NR2M1R mult_mult_12_U32 ( .A(mult_mult_12_n22), .B(mult_mult_12_n10), .Z(
        mult_mult_12_ab_6__1_) );
  NR2M1R mult_mult_12_U31 ( .A(mult_mult_12_n9), .B(mult_mult_12_n23), .Z(
        mult_mult_12_ab_7__0_) );
  XOR2M2RA mult_mult_12_U30 ( .A(mult_mult_12_ab_1__6_), .B(
        mult_mult_12_ab_0__7_), .Z(mult_mult_12_SUMB_1__6_) );
  XOR2M2RA mult_mult_12_U29 ( .A(mult_mult_12_ab_1__5_), .B(
        mult_mult_12_ab_0__6_), .Z(mult_mult_12_SUMB_1__5_) );
  XOR2M2RA mult_mult_12_U28 ( .A(mult_mult_12_ab_1__4_), .B(
        mult_mult_12_ab_0__5_), .Z(mult_mult_12_SUMB_1__4_) );
  XOR2M2RA mult_mult_12_U27 ( .A(mult_mult_12_ab_1__3_), .B(
        mult_mult_12_ab_0__4_), .Z(mult_mult_12_SUMB_1__3_) );
  XOR2M2RA mult_mult_12_U26 ( .A(mult_mult_12_ab_1__2_), .B(
        mult_mult_12_ab_0__3_), .Z(mult_mult_12_SUMB_1__2_) );
  XOR2M2RA mult_mult_12_U25 ( .A(mult_mult_12_ab_1__1_), .B(
        mult_mult_12_ab_0__2_), .Z(mult_mult_12_SUMB_1__1_) );
  XOR2M2RA mult_mult_12_U24 ( .A(mult_mult_12_ab_1__0_), .B(
        mult_mult_12_ab_0__1_), .Z(prodToAdd[1]) );
  INVM2R mult_mult_12_U23 ( .A(weightToMult[7]), .Z(mult_mult_12_n9) );
  INVM2R mult_mult_12_U22 ( .A(activationToMult[6]), .Z(mult_mult_12_n17) );
  INVM2R mult_mult_12_U21 ( .A(weightToMult[6]), .Z(mult_mult_12_n10) );
  INVM2R mult_mult_12_U20 ( .A(activationToMult[5]), .Z(mult_mult_12_n18) );
  INVM2R mult_mult_12_U19 ( .A(weightToMult[5]), .Z(mult_mult_12_n11) );
  INVM2R mult_mult_12_U18 ( .A(activationToMult[4]), .Z(mult_mult_12_n19) );
  INVM2R mult_mult_12_U17 ( .A(weightToMult[4]), .Z(mult_mult_12_n12) );
  INVM2R mult_mult_12_U16 ( .A(activationToMult[3]), .Z(mult_mult_12_n20) );
  INVM2R mult_mult_12_U15 ( .A(weightToMult[3]), .Z(mult_mult_12_n13) );
  INVM2R mult_mult_12_U14 ( .A(activationToMult[2]), .Z(mult_mult_12_n21) );
  INVM2R mult_mult_12_U13 ( .A(weightToMult[2]), .Z(mult_mult_12_n14) );
  INVM2R mult_mult_12_U12 ( .A(activationToMult[1]), .Z(mult_mult_12_n22) );
  INVM2R mult_mult_12_U11 ( .A(weightToMult[1]), .Z(mult_mult_12_n15) );
  INVM2R mult_mult_12_U10 ( .A(activationToMult[0]), .Z(mult_mult_12_n23) );
  INVM2R mult_mult_12_U9 ( .A(weightToMult[0]), .Z(mult_mult_12_n16) );
  NR2B1M2R mult_mult_12_U8 ( .NA(activationToMult[7]), .B(mult_mult_12_n16), 
        .Z(mult_mult_12_ab_0__7_) );
  AN2M2R mult_mult_12_U7 ( .A(mult_mult_12_ab_0__6_), .B(mult_mult_12_ab_1__5_), .Z(mult_mult_12_n8) );
  AN2M2R mult_mult_12_U6 ( .A(mult_mult_12_ab_0__1_), .B(mult_mult_12_ab_1__0_), .Z(mult_mult_12_n7) );
  AN2M2R mult_mult_12_U5 ( .A(mult_mult_12_ab_0__2_), .B(mult_mult_12_ab_1__1_), .Z(mult_mult_12_n6) );
  AN2M2R mult_mult_12_U4 ( .A(mult_mult_12_ab_0__3_), .B(mult_mult_12_ab_1__2_), .Z(mult_mult_12_n5) );
  AN2M2R mult_mult_12_U3 ( .A(mult_mult_12_ab_0__4_), .B(mult_mult_12_ab_1__3_), .Z(mult_mult_12_n4) );
  AN2M2R mult_mult_12_U2 ( .A(mult_mult_12_ab_0__5_), .B(mult_mult_12_ab_1__4_), .Z(mult_mult_12_n3) );
  XOR3M2RA mult_mult_12_S2_2_5 ( .A(mult_mult_12_ab_2__5_), .B(mult_mult_12_n8), .C(mult_mult_12_SUMB_1__6_), .Z(mult_mult_12_SUMB_2__5_) );
  ADFM2RA mult_mult_12_S2_2_4 ( .A(mult_mult_12_ab_2__4_), .B(mult_mult_12_n3), 
        .CI(mult_mult_12_SUMB_1__5_), .CO(mult_mult_12_CARRYB_2__4_), .S(
        mult_mult_12_SUMB_2__4_) );
  ADFM2RA mult_mult_12_S2_2_3 ( .A(mult_mult_12_ab_2__3_), .B(mult_mult_12_n4), 
        .CI(mult_mult_12_SUMB_1__4_), .CO(mult_mult_12_CARRYB_2__3_), .S(
        mult_mult_12_SUMB_2__3_) );
  ADFM2RA mult_mult_12_S2_2_2 ( .A(mult_mult_12_ab_2__2_), .B(mult_mult_12_n5), 
        .CI(mult_mult_12_SUMB_1__3_), .CO(mult_mult_12_CARRYB_2__2_), .S(
        mult_mult_12_SUMB_2__2_) );
  ADFM2RA mult_mult_12_S2_2_1 ( .A(mult_mult_12_ab_2__1_), .B(mult_mult_12_n6), 
        .CI(mult_mult_12_SUMB_1__2_), .CO(mult_mult_12_CARRYB_2__1_), .S(
        mult_mult_12_SUMB_2__1_) );
  ADFM2RA mult_mult_12_S1_2_0 ( .A(mult_mult_12_ab_2__0_), .B(mult_mult_12_n7), 
        .CI(mult_mult_12_SUMB_1__1_), .CO(mult_mult_12_CARRYB_2__0_), .S(
        prodToAdd[2]) );
  ADFM2RA mult_mult_12_S2_3_4 ( .A(mult_mult_12_ab_3__4_), .B(
        mult_mult_12_CARRYB_2__4_), .CI(mult_mult_12_SUMB_2__5_), .S(
        mult_mult_12_SUMB_3__4_) );
  ADFM2RA mult_mult_12_S2_3_3 ( .A(mult_mult_12_ab_3__3_), .B(
        mult_mult_12_CARRYB_2__3_), .CI(mult_mult_12_SUMB_2__4_), .CO(
        mult_mult_12_CARRYB_3__3_), .S(mult_mult_12_SUMB_3__3_) );
  ADFM2RA mult_mult_12_S2_3_2 ( .A(mult_mult_12_ab_3__2_), .B(
        mult_mult_12_CARRYB_2__2_), .CI(mult_mult_12_SUMB_2__3_), .CO(
        mult_mult_12_CARRYB_3__2_), .S(mult_mult_12_SUMB_3__2_) );
  ADFM2RA mult_mult_12_S2_3_1 ( .A(mult_mult_12_ab_3__1_), .B(
        mult_mult_12_CARRYB_2__1_), .CI(mult_mult_12_SUMB_2__2_), .CO(
        mult_mult_12_CARRYB_3__1_), .S(mult_mult_12_SUMB_3__1_) );
  ADFM2RA mult_mult_12_S1_3_0 ( .A(mult_mult_12_ab_3__0_), .B(
        mult_mult_12_CARRYB_2__0_), .CI(mult_mult_12_SUMB_2__1_), .CO(
        mult_mult_12_CARRYB_3__0_), .S(prodToAdd[3]) );
  ADFM2RA mult_mult_12_S2_4_3 ( .A(mult_mult_12_ab_4__3_), .B(
        mult_mult_12_CARRYB_3__3_), .CI(mult_mult_12_SUMB_3__4_), .S(
        mult_mult_12_SUMB_4__3_) );
  ADFM2RA mult_mult_12_S2_4_2 ( .A(mult_mult_12_ab_4__2_), .B(
        mult_mult_12_CARRYB_3__2_), .CI(mult_mult_12_SUMB_3__3_), .CO(
        mult_mult_12_CARRYB_4__2_), .S(mult_mult_12_SUMB_4__2_) );
  ADFM2RA mult_mult_12_S2_4_1 ( .A(mult_mult_12_ab_4__1_), .B(
        mult_mult_12_CARRYB_3__1_), .CI(mult_mult_12_SUMB_3__2_), .CO(
        mult_mult_12_CARRYB_4__1_), .S(mult_mult_12_SUMB_4__1_) );
  ADFM2RA mult_mult_12_S1_4_0 ( .A(mult_mult_12_ab_4__0_), .B(
        mult_mult_12_CARRYB_3__0_), .CI(mult_mult_12_SUMB_3__1_), .CO(
        mult_mult_12_CARRYB_4__0_), .S(prodToAdd[4]) );
  ADFM2RA mult_mult_12_S2_5_2 ( .A(mult_mult_12_ab_5__2_), .B(
        mult_mult_12_CARRYB_4__2_), .CI(mult_mult_12_SUMB_4__3_), .S(
        mult_mult_12_SUMB_5__2_) );
  ADFM2RA mult_mult_12_S2_5_1 ( .A(mult_mult_12_ab_5__1_), .B(
        mult_mult_12_CARRYB_4__1_), .CI(mult_mult_12_SUMB_4__2_), .CO(
        mult_mult_12_CARRYB_5__1_), .S(mult_mult_12_SUMB_5__1_) );
  ADFM2RA mult_mult_12_S1_5_0 ( .A(mult_mult_12_ab_5__0_), .B(
        mult_mult_12_CARRYB_4__0_), .CI(mult_mult_12_SUMB_4__1_), .CO(
        mult_mult_12_CARRYB_5__0_), .S(prodToAdd[5]) );
  ADFM2RA mult_mult_12_S2_6_1 ( .A(mult_mult_12_ab_6__1_), .B(
        mult_mult_12_CARRYB_5__1_), .CI(mult_mult_12_SUMB_5__2_), .S(
        mult_mult_12_SUMB_6__1_) );
  ADFM2RA mult_mult_12_S1_6_0 ( .A(mult_mult_12_ab_6__0_), .B(
        mult_mult_12_CARRYB_5__0_), .CI(mult_mult_12_SUMB_5__1_), .CO(
        mult_mult_12_CARRYB_6__0_), .S(prodToAdd[6]) );
  ADFM2RA mult_mult_12_S4_0 ( .A(mult_mult_12_ab_7__0_), .B(
        mult_mult_12_CARRYB_6__0_), .CI(mult_mult_12_SUMB_6__1_), .S(
        prodToAdd[7]) );
  ADFM2RA add_r67_U1_0 ( .A(pSumToAdd[0]), .B(prodToAdd[0]), .CI(1'b0), .CO(
        add_r67_carry[1]), .S(outPartialSum[0]) );
  ADFM2RA add_r67_U1_1 ( .A(pSumToAdd[1]), .B(prodToAdd[1]), .CI(
        add_r67_carry[1]), .CO(add_r67_carry[2]), .S(outPartialSum[1]) );
  ADFM2RA add_r67_U1_2 ( .A(pSumToAdd[2]), .B(prodToAdd[2]), .CI(
        add_r67_carry[2]), .CO(add_r67_carry[3]), .S(outPartialSum[2]) );
  ADFM2RA add_r67_U1_3 ( .A(pSumToAdd[3]), .B(prodToAdd[3]), .CI(
        add_r67_carry[3]), .CO(add_r67_carry[4]), .S(outPartialSum[3]) );
  ADFM2RA add_r67_U1_4 ( .A(pSumToAdd[4]), .B(prodToAdd[4]), .CI(
        add_r67_carry[4]), .CO(add_r67_carry[5]), .S(outPartialSum[4]) );
  ADFM2RA add_r67_U1_5 ( .A(pSumToAdd[5]), .B(prodToAdd[5]), .CI(
        add_r67_carry[5]), .CO(add_r67_carry[6]), .S(outPartialSum[5]) );
  ADFM2RA add_r67_U1_6 ( .A(pSumToAdd[6]), .B(prodToAdd[6]), .CI(
        add_r67_carry[6]), .CO(add_r67_carry[7]), .S(outPartialSum[6]) );
  ADFM2RA add_r67_U1_7 ( .A(pSumToAdd[7]), .B(prodToAdd[7]), .CI(
        add_r67_carry[7]), .CO(add_r67_carry[8]), .S(outPartialSum[7]) );
  ADFM2RA add_r67_U1_8 ( .A(pSumToAdd[8]), .B(1'b0), .CI(add_r67_carry[8]), 
        .CO(add_r67_carry[9]), .S(outPartialSum[8]) );
  ADFM2RA add_r67_U1_9 ( .A(pSumToAdd[9]), .B(1'b0), .CI(add_r67_carry[9]), 
        .CO(add_r67_carry[10]), .S(outPartialSum[9]) );
  ADFM2RA add_r67_U1_10 ( .A(pSumToAdd[10]), .B(1'b0), .CI(add_r67_carry[10]), 
        .CO(add_r67_carry[11]), .S(outPartialSum[10]) );
  ADFM2RA add_r67_U1_11 ( .A(pSumToAdd[11]), .B(1'b0), .CI(add_r67_carry[11]), 
        .CO(add_r67_carry[12]), .S(outPartialSum[11]) );
  ADFM2RA add_r67_U1_12 ( .A(pSumToAdd[12]), .B(1'b0), .CI(add_r67_carry[12]), 
        .CO(add_r67_carry[13]), .S(outPartialSum[12]) );
  ADFM2RA add_r67_U1_13 ( .A(pSumToAdd[13]), .B(1'b0), .CI(add_r67_carry[13]), 
        .CO(add_r67_carry[14]), .S(outPartialSum[13]) );
  ADFM2RA add_r67_U1_14 ( .A(pSumToAdd[14]), .B(1'b0), .CI(add_r67_carry[14]), 
        .CO(add_r67_carry[15]), .S(outPartialSum[14]) );
  ADFM2RA add_r67_U1_15 ( .A(pSumToAdd[15]), .B(1'b0), .CI(add_r67_carry[15]), 
        .CO(add_r67_carry[16]), .S(outPartialSum[15]) );
  ADFM2RA add_r67_U1_16 ( .A(pSumToAdd[16]), .B(1'b0), .CI(add_r67_carry[16]), 
        .CO(add_r67_carry[17]), .S(outPartialSum[16]) );
  ADFM2RA add_r67_U1_17 ( .A(pSumToAdd[17]), .B(1'b0), .CI(add_r67_carry[17]), 
        .CO(add_r67_carry[18]), .S(outPartialSum[17]) );
  ADFM2RA add_r67_U1_18 ( .A(pSumToAdd[18]), .B(1'b0), .CI(add_r67_carry[18]), 
        .CO(add_r67_carry[19]), .S(outPartialSum[18]) );
  ADFM2RA add_r67_U1_19 ( .A(pSumToAdd[19]), .B(1'b0), .CI(add_r67_carry[19]), 
        .CO(add_r67_carry[20]), .S(outPartialSum[19]) );
  ADFM2RA add_r67_U1_20 ( .A(pSumToAdd[20]), .B(1'b0), .CI(add_r67_carry[20]), 
        .CO(add_r67_carry[21]), .S(outPartialSum[20]) );
  ADFM2RA add_r67_U1_21 ( .A(pSumToAdd[21]), .B(1'b0), .CI(add_r67_carry[21]), 
        .CO(add_r67_carry[22]), .S(outPartialSum[21]) );
  ADFM2RA add_r67_U1_22 ( .A(pSumToAdd[22]), .B(1'b0), .CI(add_r67_carry[22]), 
        .CO(add_r67_carry[23]), .S(outPartialSum[22]) );
  ADFM2RA add_r67_U1_23 ( .A(pSumToAdd[23]), .B(1'b0), .CI(add_r67_carry[23]), 
        .CO(add_r67_carry[24]), .S(outPartialSum[23]) );
  ADFM2RA add_r67_U1_24 ( .A(pSumToAdd[24]), .B(1'b0), .CI(add_r67_carry[24]), 
        .CO(add_r67_carry[25]), .S(outPartialSum[24]) );
  ADFM2RA add_r67_U1_25 ( .A(pSumToAdd[25]), .B(1'b0), .CI(add_r67_carry[25]), 
        .CO(add_r67_carry[26]), .S(outPartialSum[25]) );
  ADFM2RA add_r67_U1_26 ( .A(pSumToAdd[26]), .B(1'b0), .CI(add_r67_carry[26]), 
        .CO(add_r67_carry[27]), .S(outPartialSum[26]) );
  ADFM2RA add_r67_U1_27 ( .A(pSumToAdd[27]), .B(1'b0), .CI(add_r67_carry[27]), 
        .CO(add_r67_carry[28]), .S(outPartialSum[27]) );
  ADFM2RA add_r67_U1_28 ( .A(pSumToAdd[28]), .B(1'b0), .CI(add_r67_carry[28]), 
        .CO(add_r67_carry[29]), .S(outPartialSum[28]) );
  ADFM2RA add_r67_U1_29 ( .A(pSumToAdd[29]), .B(1'b0), .CI(add_r67_carry[29]), 
        .CO(add_r67_carry[30]), .S(outPartialSum[29]) );
  ADFM2RA add_r67_U1_30 ( .A(pSumToAdd[30]), .B(1'b0), .CI(add_r67_carry[30]), 
        .CO(add_r67_carry[31]), .S(outPartialSum[30]) );
  ADFM2RA add_r67_U1_31 ( .A(pSumToAdd[31]), .B(1'b0), .CI(add_r67_carry[31]), 
        .S(outPartialSum[31]) );
endmodule

