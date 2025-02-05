#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
Python script to analyse Clonal KO RCP-PCR result.
"""
import sys
import re
import os
import pickle
import ast
import json
import numpy as np
import math
import xlrd
import pprint

def main(dat,info,strand,abundance_threashold,di,p):
    big_d = reading(dat)
    info_d= csv2dict(info)
    #pprint.pprint(info_d)
    #pprint.pprint(big_d)
    heatmap_d, bar_d= get_top_profiles(big_d,info_d,di,abundance_threashold)
    #pprint.pprint(LL_for_R)
    #for target in heatmap_d:
        #if not os.path.isdir('%s/csv/%s'%(di,target)):
        #    os.makedirs('%s/csv/%s'%(di,target))
        #Fname_h = "%s/csv/%s/heatmap.csv"%(di,target)
        #Fname_b = "%s/csv/%s/barplot.csv"%(di,target)
        #LL2csv(heatmap_d[target],Fname_h)
        #LL2csv(bar_d[target],Fname_b)
        #PDF_name = ("%s/pdf/%s_plot.pdf"%(di,target))
        #os.system("Rscript %srcppcr_ko_heatmap.r %s %s %s"%(p,Fname_b,Fname_h,PDF_name))


def get_top_profiles(dat,info,di,abundance_threashold):
    out_dat = {}
    out_bar = {}
    LL_for_csv = [["Target","Plate","Row","Col","Plate_Pos","Total_reads","#Mutation_profiles_above_threashold","Well_KO_stat","Reads_support_stat(%)", "Profile#1","#Reads#1_rate","Standard_Error#1","Profile#1_detail", "Profile#2","#Reads#2_rate","Standard_Error#2","Profile#2_detail","Profile#3","#Reads#3_rate","Standard_Error#3","Profile#3_detail","Profile#4","#Reads#4_rate","Standard_Error#4","Profile#4_detail"  ]  ]


    SUM = {}
    F = {}
    for target_site in dat:
        F[target_site] ={}
        #print target_site,
        out_dat[target_site] = []
        out_bar[target_site] = []

        out_dat[target_site].append( ["SampleID","base_index","Char_stat","ORDER"])
        out_bar[target_site].append( ["SampleID","Ratio","SE","ORDER"])

        SUM[target_site] = {}
        #print tot_reads
        count = 0
        COUNTS = 0
        gRNA_s = int(info[target_site]["gRNA_s"])
        gRNA_e = int(info[target_site]["gRNA_e"])

        temp_dat = []
        temp_bar = []
        for char in range(len(info[target_site]["Target_seq"])):
            char_stat = "-"
            PAM_frd_G = 0
            PAM_frd_C = 0
            PAM_rvs_G = 0
            PAM_rvs_C = 0
            if (gRNA_s <= (char+1) <=gRNA_e):
                char_stat = "gRNA"
            temp_dat.append( ["Reference (%s)"%(target_site),char, char_stat,COUNTS])
        p = 0
        #print target_site, info[target_site]["Target_seq"][gRNA_s-4 : gRNA_e+4]
        if (info[target_site]["Target_seq"][gRNA_s-3 -1 : gRNA_s-2 ] == "CC"):
            temp_dat[gRNA_s-3] = ["Reference (%s)"%(target_site), gRNA_s-3, "PAM",COUNTS]
            temp_dat[gRNA_s-2] = ["Reference (%s)"%(target_site), gRNA_s-2, "PAM",COUNTS]
            temp_dat[gRNA_s-1] = ["Reference (%s)"%(target_site), gRNA_s-1, "PAM",COUNTS]
            p +=1

        elif (info[target_site]["Target_seq"][gRNA_e+2-1 : gRNA_e+3] == "GG"):
            temp_dat[gRNA_e+1] = ["Reference (%s)"%(target_site), gRNA_e+1, "PAM",COUNTS]
            temp_dat[gRNA_e+2] = ["Reference (%s)"%(target_site), gRNA_e+2, "PAM",COUNTS]
            temp_dat[gRNA_e+3] = ["Reference (%s)"%(target_site), gRNA_e+3, "PAM",COUNTS]
        else:
            print "Error: NO PAM for %s" %target_site
            #print info[target_site]["Target_seq"][gRNA_s-3-1: gRNA_e+3-1]
            #print info[target_site]["Target_seq"][gRNA_s-3-1: gRNA_s-2-1]
            #print info[target_site]["Target_seq"][gRNA_e+2-1: gRNA_e+3-1]
        out_dat[target_site].append( ["Reference (%s)"%(target_site), -30, "Ref", COUNTS])
        out_bar[target_site].append( ["Reference (%s)"%(target_site),0, 0, COUNTS]  )
        COUNTS -=1
        if p ==1:
            MOVE = gRNA_s
            F[target_site] = gRNA_s
        else:
            MOVE = gRNA_e
            F[target_site] = gRNA_e

        for l in temp_dat:
            if abs(l[1]-MOVE) <= 30:
                out_dat[target_site].append( [l[0],l[1]-MOVE,l[2],l[3]] )
        for l in temp_bar:
            if abs(l[1]-MOVE) <= 30:
                out_bar[target_site].append([l[0],l[1],l[2]])
        PROFILES = {}
        PROF_ID = 1
        HIT_RATE_MEM = {}
        HIT_MEM = {}
        for plate in dat[target_site]:
            #print plate,
            for row in dat[target_site][plate]:
                #print row
                for col in dat[target_site][plate][row]:
                    try:
                        L = []

                        Well_KO_stat = "-"
                        target_loci = dat[target_site][plate][row][col][strand]




                        prof = 0
                        sum_of_hits = 0
                        profiles       = []
                        #Frameshift = "WT"
                        for mutation_profile in dat[target_site][plate][row][col][strand]:
                            if dat[target_site][plate][row][col][strand][mutation_profile] == 1:
                                dat[target_site][plate][row][col][strand] = removekey(dat[target_site][plate][row][col][strand],mutation_profile)
                        tot_reads = sum(dat[target_site][plate][row][col][strand].values())
                        if tot_reads != 0:
                            L += [target_site,plate,row,col,BR96_convert(row,col),tot_reads]



                            for mutation_profile in dat[target_site][plate][row][col][strand]:
                                Frameshift = "WT"
                                hits = dat[target_site][plate][row][col][strand][mutation_profile]
                                if hits > 1:
                                    hit_rat , error = ErrorProp_div(hits,tot_reads)
                                    imputed_hitrate = hit_rat-error


                                     #print mutation_profile, imputed_hitrate
                                    if (imputed_hitrate >= abundance_threashold) :
                                        prof +=1
                                        count +=1
                                         #print target_site,plate
                                         #print target_site,plate,row,col,tot_reads,hits,imputed_hitrate, mutation_profile
                                        sum_of_hits += hits

                                        if prof == 1:
                                            out_dat[target_site].append( ["%s_%s_%s______________________________________________________"%(plate,row,col), 0, "Ref",COUNTS ])
                                            out_bar[target_site].append( ["%s_%s_%s______________________________________________________"%(plate,row,col), 0, 0 ,COUNTS])
                                            COUNTS -=1
                                        mut_l = btop_deconvolute(info[target_site]["Target_seq"],mutation_profile)
                                        for char in range(len(mut_l)):
                                            out_dat[target_site].append( ["%s_%s_%s_Profile#%d"%(plate,row,col,prof), char +1,  mut_l[char],COUNTS ])
                                        if mut_l.count("Del") > 0:
                                            if (mut_l.count("Del")%3 != 0):
                                                Frameshift = "Indel(frameshift)"
                                            else:
                                                Frameshift = "Indel(non-frameshift)"
                                        if mut_l.count("Ins") >0:
                                            if (mut_l.count("Ins")%3 != 0):
                                                Frameshift = "Indel(frameshift)"
                                            else:
                                                Frameshift = "Indel(non-frameshift)"
                                        profiles += [Frameshift, round(hit_rat,2)*100,round(error,2)*100,mutation_profile ]


                                        out_dat[target_site].append( ["%s_%s_%s_Profile#%d"%(plate,row,col,prof), 0,  Frameshift,COUNTS ])
                                        out_bar[target_site].append( ["%s_%s_%s_Profile#%d"%(plate,row,col,prof), hit_rat,  error,COUNTS ])
                                        COUNTS -=1

                            wt = profiles.count("WT")
                            frameshift = profiles.count("Indel(frameshift)")
                            indel = profiles.count("Indel(non-frameshift)")

                            total_profs = wt+frameshift+ indel

                            if total_profs == 2:
                                if frameshift ==2:
                                    Well_KO_stat = "Homo-frameshift"
                                if indel ==2:
                                    Well_KO_stat = "Homo-indel(non-frameshift)"
                                if wt ==1:
                                    Well_KO_stat = "Hetero"
                            if total_profs==1:
                                if wt ==1:
                                    Well_KO_stat = "WT"
                                if frameshift ==1:
                                    Well_KO_stat = "Frameshift(1profile)"
                                if indel ==1:
                                    Well_KO_stat = "Indel(1profile)"
                            if total_profs > 2:
                                Well_KO_stat = "Too many profiles"



                            L += [ total_profs,Well_KO_stat,float(sum_of_hits)/tot_reads*100 ]
                            L += profiles
                            LL_for_csv.append(L)
                    except KeyError:
                        pass
    LL2csv(LL_for_csv,"%s/%s_sumary.csv"%(di,di.split("Log_")[1] ))
    return out_dat, out_bar

################################
#### Small functions
################################

def fx(x):
    return x



def csv2dict(f_name):
    d = {}
    with open(f_name,"r") as F:
        c =0
        for line in F:
            c+=1
            cols = line.split(",")
            #print cols
            if (c ==1):
                header = cols
            else:
                d[cols[0]] = {}
                for i in range(len(header[2:])+1):
                    d[cols[0]][header[i+1].split("\n")[0]] =cols[i+1].split("\n")[0]

    return d

def LL2csv(LL,name):
    with open(name,"w") as F:
        for L in LL:
            F.write("%s\n" %  (",").join( [str(i) for i in L]))
    F.close()



def ErrorProp_div(Hit,All):
    val = 0
    error = 0

    Hit = float(Hit)
    All = float(All)


    val = Hit/All
    d_All = All **(0.5)
    #print All,d_All
    d_Hit = Hit **(0.5)
    #print target, d_target
    error = ((d_All/All) ** 2) + ((d_Hit/Hit) ** 2)
    error **= 0.5
    error  *= val

    return (val,error);

def reading(name):
    with open(name, 'r') as F:
        ob_from_file = eval(F.read())
    F.close()
    return ob_from_file

def btop_deconvolute(target,btop):
    btop_l = [a for a in  re.split('(\d+)',btop) if (len(a) > 0)]

    mut_mem = [] #for showing % in heatmap
    #print btop_l
    for i in btop_l:
        try:
            mut_mem += ["-" for i in range(0,int(i))]
            #print len(mut_mem),mut_mem
        except ValueError:
            Mut = [i[j:j+2] for j in range(0, len(i), 2)]
            #print Mut
            for m in Mut:
                if m[0] == "-":
                    mut_mem.append("Del")
                elif m[1] == "-":
                    mut_mem.append("Ins")
                else:
                    mut_mem.append("Mut")
    #print len(target),len(mut_mem)
    return mut_mem

def removekey(d, key):
    r = dict(d)
    del r[key]
    return r

def list2combinatoral(l1,l2):
    l =[]
    for i1 in l1:
         for i2 in l2:
             i = ("-").join([i1,i2])
             l.append(i)
    return l
def rc_pcr_coordinate(POS):
    if POS[2:] == "96":
        if POS[0] == "T":
            ROW = ["R01","R03","R05","R07","R09","R11","R13","R15"]
        if POS[0] == "B":
            ROW = ["R02","R04","R06","R08","R10","R12","R14","R16"]
        if POS[1] == "L":
            COL = ["C01","C03","C05","C07","C09","C11","C13","C15","C17","C19","C21","C23"]
        if POS[1] == "R":
            COL = ["C02","C04","C06","C08","C10","C12","C14","C16","C18","C20","C22","C24"]
    return ROW, COL
def summary2dict(summary,D):
    c=0
    with open(summary,"r") as F:
        for line in F:
            c +=1
            cols = line.split("\n")[0].split(",")
            #print cols
            if c ==1:
                keys = cols[4:]
            else:
                try:
                    for key in range(len(keys)):
                        try:
                            D[cols[0]][cols[1]][("-").join([cols[2],cols[3]])][keys[key]] = cols[key+4]
                        except IndexError:
                            D[cols[0]][cols[1]][("-").join([cols[2],cols[3]])][keys[key]] = ""

                    #D[cols[0]][cols[1]][("-").join([cols[2],cols[3]])]["Cell_viability"]="N.A."
                except KeyError:
                    pass
        F.close()
    return D

def extract_targets(f):
    targets = []
    with open(f,"r") as F:
        c = 1
        for line in F:
            if c > 1:
                cols = line.split(",")
                targets.append(cols[0])
            c+=1
        F.close()
    return targets


def read_viability_files(directory,corrd,D):

    l = get_xlsx(directory)
    for target in D:
        for plate in D[target]:
            xlsx = [ i for i in l if target in i]
            #print xlsx,target,plate
            if len(xlsx) ==0:
                try:
                    D = removekey(D,target)
                except KeyError:
                    pass
            elif len(xlsx) ==1:
                book = xlrd.open_workbook("%s/%s"%(directory,xlsx[0]))
                sh = book.sheet_by_index(0)
                for well in D[target][plate]:
                    r,c,pos = xlsx_pos_BR96_convert(well)
                    D[target][plate][well]["Cell_viability"] = sh.cell_value(rowx=r-1, colx=c-1)
            elif len(xlsx) > 1:
                print "Too many .xlsx files for Target: %s || %s"%(target,str(xlsx))
    return D


def get_xlsx(x):
    files = []
    lis = os.listdir("%s" %x)
    for i in lis:
        if i[-5:] == ".xlsx" :
            if i[0] != "~":
                files.append(i)
    return files

def xlsx_pos_TR96_convert(well):
    r = well.split("-")[0]
    c = well.split("-")[1]

    R = {"R01":4,"R03":5,"R05":6,"R07":7,"R09":8,"R11":9,"R13":10,"R15":11}
    C = {"C02":2,"C04":3,"C06":4,"C08":5,"C10":6,"C12":7,"C14":8,"C16":9,"C18":10,"C20":11,"C22":12,"C24":13}

    posR = {"R01":"A","R03":"B","R05":"C","R07":"D","R09":"E","R11":"F","R13":"G","R15":"H"}
    posC = {"C02":1,"C04":2,"C06":3,"C08":4,"C10":5,"C12":6,"C14":7,"C16":8,"C18":9,"C20":10,"C22":11,"C24":12}
    pos  = ("").join([posR[r],str(posC[c])])
    return R[r],C[c],pos
def TR96_convert(PosR,PosC):
    posR = {"R01":"A","R03":"B","R05":"C","R07":"D","R09":"E","R11":"F","R13":"G","R15":"H"}
    posC = {"C02":1,"C04":2,"C06":3,"C08":4,"C10":5,"C12":6,"C14":7,"C16":8,"C18":9,"C20":10,"C22":11,"C24":12}
    pos  = ("").join([posR[PosR],str(posC[PosC])])
    return pos

def BR96_convert(PosR,PosC):
    posR = {"R02":"A","R04":"B","R06":"C","R08":"D","R10":"E","R12":"F","R14":"G","R16":"H"}
    posC = {"C02":1,"C04":2,"C06":3,"C08":4,"C10":5,"C12":6,"C14":7,"C16":8,"C18":9,"C20":10,"C22":11,"C24":12}
    pos  = ("").join([posR[PosR],str(posC[PosC])])
    return pos




if __name__ == '__main__':
    dat  = sys.argv[1]
    info = sys.argv[2]
    strand = sys.argv[3] #"Plus" or "Minus"
    abundance_threashold = float(sys.argv[4])#Default = 0.1
    di = sys.argv[5]#Directory name. Defalt "."
    p = sys.argv[6]
    #cellv = sys.argv[7]
    #coord = sys.argv[7]

    main(dat,info,strand,abundance_threashold,di,p)
