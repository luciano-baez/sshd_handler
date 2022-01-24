# encoding: utf-8
## #!/usr/bin/python
#
# Copyright: (c) 2020, Luciano Baez <lucianobaez@ar.ibm.com>
#                                   <lucianobaez@outlook.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#  This is a module to handle /etc/sudoers file
#
# History
#   -Ver 0.1 : Nov 04 2020

import os
import filecmp
import pwd
import grp
import platform
import subprocess
import json
import shutil
import datetime
import platform

def catfile(filename):
    f = open(filename, "r")
    text = f.read()
    print(text)
    f.close()
def gettimestampstring():
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")

def execute(cmdtoexecute,sshdlogdic):
    #executable=" su - db2inst1 -c \""+cmdtoexecute+"\""
    executable=cmdtoexecute
    stdout=""
    CmdOut = subprocess.Popen([executable], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            shell=True)
    stdout,stderr = CmdOut.communicate()
    rc = CmdOut.returncode
    if sshdlogdic['log']==True:
        logtofile(sshdlogdic['logfile'],'Excecute cmd '+cmdtoexecute+' rc:'+str(rc)+' (execute)')
    #print (stdout)
    stdoutstr= str(stdout, "utf-8")
    #(str(hexlify(b"\x13\x37"), "utf-8"))
    return stdoutstr
    #return stdout

def executefull(cmdtoexecute,sshdlogdic):
    executeresult={'stdout':'','stderr':'','rc':''}
    executable=cmdtoexecute
    stdout=""
    CmdOut = subprocess.Popen([executable], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            shell=True)
    stdout,stderr = CmdOut.communicate()
    rc = CmdOut.returncode
    executeresult['stdout']=str(stdout, "utf-8")
    executeresult['stderr']=stderr
    executeresult['rc']=rc
    if sshdlogdic['log']==True:
        #logtofile(sshdlogdic['logfile'],'Excecute out '+stdout+' ')
        #logtofile(sshdlogdic['logfile'],'Excecute err '+stderr+' ')
        logtofile(sshdlogdic['logfile'],'Excecute cmd '+cmdtoexecute+' rc:'+str(rc)+' (executefull')
    return executeresult

def executeas(cmdtoexecute,userexe,sshdlogdic):
    executable=" su - "+userexe.strip()+" -c \""+cmdtoexecute.strip().replace("\"","\\\"")+"\""
    if (userexe.strip() == "root"):
        # if user is "root" will remove the "su -" (swich user)
        executable=cmdtoexecute.strip()
    else:
        try:
            pwd.getpwnam(userexe.strip())
        except KeyError:
            # if user "userexe" doesen't exists will run as root
            executable=cmdtoexecute.strip()
    #executable=cmdtoexecute
    stdout=""
    #print(executable)
    #print(cmdtoexecute.strip())
    CmdOut = subprocess.Popen([executable], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            shell=True)
    stdout,stderr = CmdOut.communicate()
    rc = CmdOut.returncode
    if sshdlogdic['log']==True:
        logtofile(sshdlogdic['logfile'],'Excecute cmd '+cmdtoexecute+' by '+userexe+'  rc:'+str(rc)+' (executeas')
    return stdout

def getuserlist():
    resultlist=[]
    usersfile="/etc/passwd"
    if os.path.isfile(usersfile):
        with open(usersfile,"r") as sourcefh:
            line = sourcefh.readline()
            while line:
                auxline=line.replace('\n', '').strip().split(':')
                firstword=''
                if (len(auxline)>0):
                    firstword=auxline[0]
                if (firstword != ''):
                    resultlist.append(firstword)
                line = sourcefh.readline()
            sourcefh.close
    return resultlist

def getgrouplist():
    resultlist=[]
    usersfile="/etc/group"
    if os.path.isfile(usersfile):
        with open(usersfile,"r") as sourcefh:
            line = sourcefh.readline()
            while line:
                auxline=line.replace('\n', '').strip().split(':')
                firstword=''
                if (len(auxline)>0):
                    firstword=auxline[0]
                if (firstword != ''):
                    resultlist.append(firstword)
                line = sourcefh.readline()
            sourcefh.close
    return resultlist

def getsshdplatform(sshdlogdic):
    flavor=execute("uname",sshdlogdic)
    AUX=str(flavor).strip().split("\n")
    platform=AUX[0]
    if platform == "Linux":
        auxiszlinux=execute("uname -a| grep s390x|wc -l|sed 's/ //g'",sshdlogdic)
        AUX=str(auxiszlinux).strip().split("\n")
        iszlinux=int(AUX[0])
        if iszlinux>0:
            platform="zLinux"

    return platform

def getsshdversion(sshdlogdic):
    sshdversion=""
    sshdverstr=execute("/usr/bin/ssh -V",sshdlogdic)
    AUX=str(sshdverstr).strip().split("\n")
    FIRSTLINE=""
    
    if len(AUX)>0:
        FIRSTLINE=AUX[0].strip().split()
    if len(FIRSTLINE)>0:
        sshdversion=FIRSTLINE[0]
    
    return sshdversion



def getgeneralsection(configfile,sshdlogdic):
    genrealsection=[]
    with open(configfile,"r") as sourcefh:
        line = sourcefh.readline()
        found=False
        linecount=0
        while line and (found==False):
            auxline=line.replace('\n', '')
            wordlist=auxline.split()
            firstchar=''
            firstword=''
            if (len(wordlist)>0):
                firstword=wordlist[0].strip()
            if (firstword != ''):
                firstchar=firstword[0]
            if (firstword.upper()=="MATCH"):
                found=True
            if (found==False):
                #process line
                secondpart=auxline[len(firstword):len(auxline)]
                gsline={}
                if (firstchar == '#') or auxline.strip() == '':
                    gsline['key']='#'
                    #if (linecount==0) and (firstword != "#sshd_handler"):
                    #    auxgline={}
                    #    auxgline['key']='#'
                    #    auxgline['value']=''
                    #    auxgline['match']=''
                    #    #auxgline['line']='#sshd_handler File parsed'
                    #    auxgline['line']=auxline
                    #    genrealsection.append(auxgline)
                    auxgline={}
                    auxgline['key']='#'
                    auxgline['value']=''
                    auxgline['match']='general'
                    auxgline['line']=auxline
                    genrealsection.append(auxgline)

                else:
                    gsline['key']=firstword
                    gsline['value']=secondpart
                    gsline['match']='general'
                    gsline['line']=auxline
                    genrealsection.append(gsline)
                #print(firstword+"   "+secondpart+" ->"+auxline)
                #print(gsline)
            linecount=linecount+1
            line = sourcefh.readline()
        sourcefh.close
    return genrealsection

def getmatchuserssection(configfile,sshdlogdic):
    matchuserssection=[]
    with open(configfile,"r") as sourcefh:
        line = sourcefh.readline()
        matchfound=False
        section=""
        while line:
            auxline=line.replace('\n', '')
            wordlist=auxline.split()
            firstchar=''
            firstword=''
            secondword=''
            thirdword=''
            if (len(wordlist)>0):
                firstword=wordlist[0].strip()
            if (len(wordlist)>1):
                secondword=wordlist[1].strip()                
            if (firstword != ''):
                firstchar=firstword[0]
            
            if (firstword.upper()=="MATCH") and (secondword.upper()=="USER"):
                matchfound=True
                section=""
                if (len(wordlist)>2):                    
                    auxdef=auxline.split(secondword)
                    if len(auxdef)>1:
                        thirdword=auxdef[1]
                section=thirdword.strip()
            if (firstword.upper()=="MATCH") and (secondword.upper()=="GROUP"):
                matchfound=False
                
            if (matchfound==True):
                #process line
                secondpart=auxline[len(firstword):len(auxline)].strip()
                musline={}

                if (firstchar == '#') or auxline.strip() == '':
                    musline['key']='#'
                else:
                    musline['key']=firstword
                musline['value']=secondpart
                musline['match']=section
                musline['line']=auxline
                matchuserssection.append(musline)
                #print(firstword+"   "+secondpart+" ->"+auxline)
                #print(musline)
            line = sourcefh.readline()
        sourcefh.close
    return matchuserssection

def getmatchgroupssection(configfile,sshdlogdic):
    matchgroupssection=[]
    with open(configfile,"r") as sourcefh:
        line = sourcefh.readline()
        matchfound=False
        section=""
        while line:
            auxline=line.replace('\n', '')
            wordlist=auxline.split()
            firstchar=''
            firstword=''
            secondword=''
            thirdword=''
            if (len(wordlist)>0):
                firstword=wordlist[0].strip()
            if (len(wordlist)>1):
                secondword=wordlist[1].strip()                
            if (firstword != ''):
                firstchar=firstword[0]
            
            if (firstword.upper()=="MATCH") and (secondword.upper()=="USER"):
                matchfound=False
            if (firstword.upper()=="MATCH") and (secondword.upper()=="GROUP"):
                matchfound=True
                if (len(wordlist)>2):                    
                    auxdef=auxline.split(secondword)
                    if len(auxdef)>1:
                        thirdword=auxdef[1]
                section=thirdword.strip()

            if (matchfound==True):
                #process line
                secondpart=auxline[len(firstword):len(auxline)].strip()
                mgsline={}
                if (firstchar == '#') or auxline.strip() == '':
                    mgsline['key']='#'
                else:
                    mgsline['key']=firstword
                mgsline['value']=secondpart
                mgsline['match']=section
                mgsline['line']=auxline
                matchgroupssection.append(mgsline)
                #print(firstword+"   "+secondpart+" ->"+auxline)
                #print(mgsline)
            line = sourcefh.readline()
        sourcefh.close
    return matchgroupssection
    
def getsshd_fact(sshdlogdic):
    sshdDIC= {'installed':False,'installed':False,'platform': '','version': '', 'stable': '', 'binfile': '','cfgfie': '','generalsection': {},'matchusers': [],'matchgroups': []}

    sshdDIC['platform']=getsshdplatform(sshdlogdic)
    RC=getsshdinstalled(sshdDIC['platform'],sshdlogdic)
    #print(RC)
    if (RC['rc'] == 0):
        sshdDIC['installed']=True
        sshdDIC['server']=platform.uname()[1]
        sshdDIC['version']=getsshdversion(sshdlogdic)
        sshdDIC['stable']=validatesshd(sshdDIC['platform'],sshdlogdic)
        sshdDIC['binfile']="/usr/sbin/sshd"
        sshdDIC['cfgfie']="/etc/ssh/sshd_config"
        sshdDIC['generalsection']=getgeneralsection(sshdDIC['cfgfie'],sshdlogdic)
        sshdDIC['matchusers']=getmatchuserssection(sshdDIC['cfgfie'],sshdlogdic)
        sshdDIC['matchgroups']=getmatchgroupssection(sshdDIC['cfgfie'],sshdlogdic)
        #print (sshdDIC['matchgroups'])
    #print("")
    return sshdDIC

def savesshd_configtofile(filetosave,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    if os.path.isfile(filetosave):
        resultcode['rc']=1
        resultcode['stdout']='ERR - File exists'
    else:
        with open(filetosave,"w") as cfgsave:
            #print(sshdfact['generalsection'])
            #General Section
            auxgeneral=sshdfact['generalsection'].copy()
            while auxgeneral:
                recgen=auxgeneral.pop(0)
                #print(recgen)
                
                cfgsave.write(recgen['line']+"\n")
                #print(recgen)

            #Match User Section
            auxuser=sshdfact['matchusers'].copy()
            #print("------")
            #print(auxuser)
            while auxuser:
                recuser=auxuser.pop(0)
                #print(recuser['line'])
                cfgsave.write(recuser['line']+"\n")

            #Match Group Section
            auxgroup=sshdfact['matchgroups'].copy()
            while auxgroup:
                recgroup=auxgroup.pop(0)
                cfgsave.write(recgroup['line']+"\n")
                #print(recgroup['line'])

            cfgsave.close
        os.chmod(filetosave, 0o644)

    return resultcode

def savesshd_config(sshdconfigbackup,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=""
    timestamp=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    #Define file names
    BACKUPFILE_sshd=sshdfact['cfgfie'].strip()+'-'+timestamp+'.bkp'
    increment=0
    while os.path.isfile(BACKUPFILE_sshd):
        increment=increment=+1
        BACKUPFILE_sshd=sshdfact['cfgfie'].strip()+'-'+timestamp+'_'+str(increment)+'.bkp'
    TEMPFILE_sshd="/tmp/sshd_config"+'-'+timestamp+'.tmp'
    increment=0
    while os.path.isfile(TEMPFILE_sshd):
        increment=increment=+1
        TEMPFILE_sshd="/tmp/sshd_config"+'-'+timestamp+'_'+str(increment)+'.tmp'
    #
    if sshdfact['installed']==True:
        if os.path.isfile(sshdfact['cfgfie']):
            os.chmod(sshdfact['cfgfie'], 0o644)
            #Take backup
            shutil.copy2(sshdfact['cfgfie'], BACKUPFILE_sshd)
            os.chmod(BACKUPFILE_sshd, 0o644)
        
        #Saving in a tmp file
        RC=savesshd_configtofile(TEMPFILE_sshd,sshdfact,sshdlogdic)
        if RC['rc']==0:
            if filecmp.cmp(TEMPFILE_sshd, sshdfact['cfgfie']) == False:    
                shutil.copy2(TEMPFILE_sshd,sshdfact['cfgfie'])
                os.chmod(sshdfact['cfgfie'], 0o644)
                validation=validatesshd(sshdfact['platform'],sshdlogdic)
                if validation>0:
                    #Validation error Rollback cfg
                    RESCODE=str(validation)
                    resultcode['rc']=4
                    if os.path.isfile(BACKUPFILE_sshd):
                        shutil.copy2(BACKUPFILE_sshd,sshdfact['cfgfie'])
                        os.chmod(sshdfact['cfgfie'], 0o644)
                        #removing unnecesary backup due rollback
                        os.remove(BACKUPFILE_sshd)
            else:
                #SSHD Nothing changed
                resultcode['rc']=5
                if os.path.isfile(BACKUPFILE_sshd):
                    #removing unnecesary backup
                    os.remove(BACKUPFILE_sshd)
        else:
            #SSHD config saving error
            resultcode['rc']=2    
    else:
        #SSHD not installed
        resultcode['rc']=1

    if not sshdconfigbackup:
        if os.path.isfile(BACKUPFILE_sshd):
            #removing unnecesary backup
            os.remove(BACKUPFILE_sshd)
        
    #removing Temp file
    #if os.path.isfile(TEMPFILE_sshd):
    #    os.remove(TEMPFILE_sshd)

            
    rcstdout=["INF: File "+sshdfact['cfgfie']+" saved successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "ERR: Error in saving (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying save the file "+sshdfact['cfgfie']+" got unstable server sshd -t = "+RESCODE+" error. Roll back Applied (rc=4).",
            "INF: No change made on "+sshdfact['cfgfie']+" file (rc=5)."
            
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode
    

def validatesshd(platform,sshdlogdic):
    resultcode=0
    if os.path.isfile('/etc/ssh/sshd_config'):
        sshdstable=execute("/usr/sbin/sshd -t 2>/dev/null 1>/dev/null; echo $?| tail -1",sshdlogdic)
        AUX=str(sshdstable).strip().split("\n")
        RESCODE=int(AUX[0].strip())
        resultcode=RESCODE
    else:
        resultcode=9999999
    return resultcode

def restartsshd(platform,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''

    if platform == "AIX":
        sshdstable=executefull("stopsrc -s sshd; sleep 3; startsrc -s sshd",sshdlogdic)
        #sshdstable=execute("stopsrc -s sshd; sleep 3; startsrc -s sshd",sshdlogdic)
        #AUX=str(sshdstable).strip().split("\n")
        #RESCODE=int(AUX[0].strip())
        #resultcode['rc']=RESCODE
        resultcode=sshdstable
    
    if platform == "Linux":
        #sshdstable=execute("systemctl restart sshd",sshdlogdic)
        sshdstable=executefull("systemctl restart sshd",sshdlogdic)
        #AUX=str(sshdstable).strip().split("\n")
        #RESCODE=int(AUX[0].strip())
        resultcode=sshdstable
    
    return resultcode


def getsshdinstalled(platform,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''

    if os.path.isfile('/usr/sbin/sshd'):
        # 
        if os.path.isfile('/etc/ssh/sshd_config'):
            RESCODE=str(validatesshd(platform,sshdlogdic))
            if RESCODE != '0':
                resultcode['rc']=2
        else:
            # 3 Dir /etc/sshd not found
            resultcode['rc']=3
    else:
        # 1 sshd not installed
        resultcode['rc']=1
    rcstdout=["INF: sshd installed (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "ERR: unstable server sshd -t = "+RESCODE+" error (rc=2).",
            "ERR: /etc/ssh/sshd_config not found (rc=3).",
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def existslineinglobal(line,section):
    resultcode={}
    resultcode['exists']=False
    resultcode['line']=0
    resultcode['tag']=''
    linetocompare=line.strip().upper()
    sec=section.copy()
    linenum=0
    #print(section)
    while sec and resultcode['exists']==False:
        s=sec.pop(0)
        if (linetocompare==s['line'].strip().upper()):
            resultcode['exists']=True
            resultcode['line']=linenum
        linenum=linenum+1
    return resultcode

def existsstartlineinglobal(line,section):
    resultcode={}
    resultcode['exists']=False
    resultcode['line']=0
    resultcode['tag']=''
    linetocompare=line.strip().upper()
    sec=section.copy()
    linenum=0
    #print(section)
    if len(linetocompare)>0:
        while sec and resultcode['exists']==False:
            s=sec.pop(0)
            #print(s)
            wordtocompare=s['line'][0:len(linetocompare)]
            #print("comparing "+linetocompare+" "+ wordtocompare)
            if (linetocompare==wordtocompare.upper()):
                resultcode['exists']=True
                resultcode['line']=linenum
            linenum=linenum+1
    return resultcode

def existsstartlineinsection(line,section,sectionkey,sectionvalue,sectionmatch):
    resultcode={}
    resultcode['exists']=False
    resultcode['line']=0
    resultcode['tag']=''
    linetocompare=line.strip().upper()
    sec=section.copy()
    linenum=0
    #print(section)
    #print("sectionmatch: "+sectionmatch)
    if len(linetocompare)>0:
        while sec and resultcode['exists']==False:
            s=sec.pop(0)
            #print(s)
            wordtocompare=s['line'][0:len(linetocompare)]
            #print("comparing "+linetocompare+" "+ wordtocompare)
            if (linetocompare==wordtocompare.upper()):
                if s['match'] != 'general':
                    #if s['key']==sectionkey and s['value']==sectionvalue and s['match']==sectionmatch:
                    if s['match']==sectionmatch:
                        resultcode['exists']=True
                        resultcode['line']=linenum
                else:
                    resultcode['exists']=True
                    resultcode['line']=linenum
            linenum=linenum+1
    return resultcode

def existslineinsection(line,match,section):
    resultcode={}
    resultcode['exists']=False
    resultcode['line']=0
    resultcode['tag']=''
    linetocompare=line.strip().upper()
    sec=section.copy()
    linenum=0
    #print(section)
    while sec and resultcode['exists']==False:
        s=sec.pop(0)
        if (s['match'].strip().upper() == match.strip().upper()):
            if (linetocompare==s['line'].strip().upper()):
                resultcode['exists']=True
                resultcode['line']=linenum
        linenum=linenum+1
    return resultcode

def existsmatchuser(user,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['exists']=False
    resultcode['tag']=''
    userstags=sshdfact['matchusers'].copy()
    users=[]
    while userstags:
        tag=userstags.pop(0)
        userlist=tag['match'].strip().split(',')
        for usr in userlist:
            userdic={}
            userdic['user']=usr
            userdic['tag']=tag['match']
            users.append(userdic)

    for userdic in users:
        if (userdic['user'].strip().upper()==user.strip().upper()):
            resultcode['exists']=True
            resultcode['tag']=userdic['tag']
    return resultcode

def existsmatchgroup(group,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['exists']=False
    resultcode['tag']=''
    groupstags=sshdfact['matchgroups'].copy()
    groups=[]
    
    while groupstags:
        tag=groupstags.pop(0)
        grouplist=tag['match'].strip().split(',')
        for grp in grouplist:
            groupdic={}
            groupdic['group']=grp
            groupdic['tag']=tag['match']
            groups.append(groupdic)

    for groupdic in groups:
        #print(groupdic)
        if (groupdic['group'].strip().upper()==group.strip().upper()):
            resultcode['exists']=True
            resultcode['tag']=groupdic['tag']

    return resultcode

def addmatchuser(user,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        exists=existsmatchuser(user,sshdfact,sshdlogdic)
        if exists['exists']==False:
            auxusr={}
            auxusr['key']="Match"
            auxusr['value']= "User"
            auxusr['match']= user
            auxusr['line']="Match User "+user
            sshdfact['matchusers'].append(auxusr)
        else:
            resultcode['rc']=2    
    else:
        resultcode['rc']=3

    rcstdout=["INF: Match user "+user+" added successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Match user "+user+" already there (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to add Match user got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def addmatchuserfirst(user,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        exists=existsmatchuser(user,sshdfact,sshdlogdic)
        if exists['exists']==False:
            auxusr={}
            auxusr['key']="Match"
            auxusr['value']= "User"
            auxusr['match']= user
            auxusr['line']="Match User "+user
            oldulist=sshdfact['matchusers']
            newulist=[]
            newulist.append(auxusr)
            newulist.extend(oldulist)
            sshdfact['matchusers']=newulist
        else:
            resultcode['rc']=2    
    else:
        resultcode['rc']=3

    rcstdout=["INF: Match user "+user+" added successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Match user "+user+" already there (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to add Match user got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def addmatchgroup(group,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        exists=existsmatchgroup(group,sshdfact,sshdlogdic)
        if exists['exists']==False:
            auxgrp={}
            auxgrp['key']="Match"
            auxgrp['value']= "Group"
            auxgrp['match']= group
            auxgrp['line']="Match Group "+group
            sshdfact['matchgroups'].append(auxgrp)
        else:
            resultcode['rc']=2    
    else:
        resultcode['rc']=3

    rcstdout=["INF: Match group "+group+" added successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Match group "+group+" already there (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to add Match group got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]

    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def addmatchgroupfirst(group,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        exists=existsmatchgroup(group,sshdfact,sshdlogdic)
        if exists['exists']==False:
            auxgrp={}
            auxgrp['key']="Match"
            auxgrp['value']= "Group"
            auxgrp['match']= group
            auxgrp['line']="Match Group "+group

            oldglist=sshdfact['matchgroups']
            newglist=[]
            newglist.append(auxgrp)
            newglist.extend(oldglist)
            sshdfact['matchgroups']=newglist

            #sshdfact['matchgroups'].append(auxgrp)
        else:
            resultcode['rc']=2    
    else:
        resultcode['rc']=3

    rcstdout=["INF: Match group "+group+" added successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Match group "+group+" already there (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to add Match group got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]

    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def removematchuser(user,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    linestodelete=[]
    deletedlines=0
    RC=existsmatchuser(user,sshdfact,sshdlogdic)
    if  RC['exists'] == True:
        postodelete=-1
        if (user.strip().upper() == RC['tag'].strip().upper()):
            #Exist a explisit Match user
            userstags=sshdfact['matchusers']
            pos=0
            for userdic in sshdfact['matchusers']:
                if (userdic['match'].strip().upper() == RC['tag'].strip().upper()):
                    #queue lines to delete
                    if postodelete==-1:
                        postodelete=pos
                    linestodelete.append(postodelete)
                pos=pos+1
        else:
            #User is part of a complex  Match user (with other users)
            userstags=sshdfact['matchusers']
            pos=0
            
            for userdic in sshdfact['matchusers']:
                value=""
                values=userdic['value'].strip().split()
                if len(values)>0:
                    value=values[0].upper()
                if (userdic['key'].strip().upper() == "MATCH") and  (value == "USER") and (userdic['match'].strip().upper() == RC['tag'].strip().upper()):
                    USERSLIST=userdic['match'].strip().split(",")
                    USERSSTRING=""
                    for usr in USERSLIST:
                        if (usr.strip().upper() != user.strip().upper()):
                            if (USERSSTRING == ""):
                                USERSSTRING=usr
                            else:
                                USERSSTRING=USERSSTRING+","+usr
                    userdic['match']=USERSSTRING
                    userdic['value']="User "+USERSSTRING
                    userdic['line']="Match User "+USERSSTRING
                pos=pos+1

        for ln in linestodelete:
            removed=sshdfact['matchusers'].pop(ln)
            #print(ln)
            #print(removed)
            deletedlines=deletedlines+1
        
    else:
        resultcode['rc']=2

    resultcode['tag']=''
    userstags=sshdfact['matchusers'].copy()
    users=[]
    while userstags:
        tag=userstags.pop(0)
        userlist=tag['match'].strip().split(',')
        for usr in userlist:
            userdic={}
            userdic['user']=usr
            userdic['tag']=tag['match']
            users.append(userdic)


    rcstdout=["INF: Match user "+user+" removed successfully (lines deleted="+str(deletedlines)+") (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Match user "+user+" isn't  there (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to remove Match user got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def removematchgroup(group,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    linestodelete=[]
    deletedlines=0
    RC=existsmatchgroup(group,sshdfact,sshdlogdic)
    if  RC['exists'] == True:
        postodelete=-1
        if (group.strip().upper() == RC['tag'].strip().upper()):
            #Exist a explisit Match group
            groupstags=sshdfact['matchgroups']
            pos=0
            for groupdic in sshdfact['matchgroups']:
                if (groupdic['match'].strip().upper() == RC['tag'].strip().upper()):
                    #queue lines to delete
                    if postodelete==-1:
                        postodelete=pos
                    linestodelete.append(postodelete)
                pos=pos+1
        else:
            #group is part of a complex  Match group (with other groups)
            groupstags=sshdfact['matchgroups']
            pos=0
            
            for groupdic in sshdfact['matchgroups']:
                value=""
                values=groupdic['value'].strip().split()
                if len(values)>0:
                    value=values[0].upper()
                if (groupdic['key'].strip().upper() == "MATCH") and  (value == "GROUP") and (groupdic['match'].strip().upper() == RC['tag'].strip().upper()):
                    GROUPSLIST=groupdic['match'].strip().split(",")
                    GROUPSSTRING=""
                    for usr in GROUPSLIST:
                        if (usr.strip().upper() != group.strip().upper()):
                            if (GROUPSSTRING == ""):
                                GROUPSSTRING=usr
                            else:
                                GROUPSSTRING=GROUPSSTRING+","+usr
                    groupdic['match']=GROUPSSTRING
                    groupdic['value']="Group "+GROUPSSTRING
                    groupdic['line']="Match Group "+GROUPSSTRING
                pos=pos+1

        for ln in linestodelete:
            removed=sshdfact['matchgroups'].pop(ln)
            #print(ln)
            #print(removed)
            deletedlines=deletedlines+1
        
    else:
        resultcode['rc']=2

    resultcode['tag']=''
    groupstags=sshdfact['matchgroups'].copy()
    groups=[]
    while groupstags:
        tag=groupstags.pop(0)
        grouplist=tag['match'].strip().split(',')
        for usr in grouplist:
            groupdic={}
            groupdic['group']=usr
            groupdic['tag']=tag['match']
            groups.append(groupdic)
    rcstdout=["INF: Match group "+group+" removed successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Match group "+group+" isn't there (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to remove Match group got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def addlinetoglobal(line,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        existline=existslineinglobal(line,sshdfact['generalsection'])
        if (existline['exists']==False):
            words=line.strip().split()
            firstword=""
            secondword=""
            if len(words)>0:
                firstword=words[0]
            if len(words)>1:
                secondword=words[1]
            auxusr={}
            auxusr['key']= firstword
            auxusr['value']= secondword
            auxusr['match']= 'general'
            auxusr['line']= line
    
            #newmatcgeneral=[]
            #oldmatchgeneral=sshdfact['generalsection'].copy()

            #sshdfact['generalsection']=newmatcgeneral
            sshdfact['generalsection'].append(auxusr)
            #for mu in sshdfact['matchusers']:
            #    print(mu)
            #print("")
        else:
            #linealready there
            resultcode['rc']=2
    
    else:
        #previous unstable
        resultcode['rc']=3

    rcstdout=["INF: Line "+line+" added to general section successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Line "+line+" already at general section (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to add a line "+line+" to a general section got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]

    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def addlinetoglobalat(position,line,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        existline=existslineinglobal(line,sshdfact['generalsection'])
        if (existline['exists']==False):
            words=line.strip().split()
            firstword=""
            secondword=""
            if len(words)>0:
                firstword=words[0]
            if len(words)>1:
                secondword=words[1]
            auxusr={}
            auxusr['key']= firstword
            auxusr['value']= secondword
            auxusr['match']= 'general'
            auxusr['line']= line
    
            sshdfact['generalsection'].insert(position,auxusr)
    
        else:
            #linealready there
            resultcode['rc']=2
    
    else:
        #previous unstable
        resultcode['rc']=3

    rcstdout=["INF: Line "+line+" added to general section successfully at position:"+str(position)+" (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Line "+line+" already at general section (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to add a line "+line+" to a general section got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]

    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def removelinefromglobal(line,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        existline=existslineinglobal(line,sshdfact['generalsection'])
        if (existline['exists']==True):
            words=line.strip().split()
            firstword=""
            secondword=""
            thirdword=""
            if len(words)>0:
                firstword=words[0]
            if len(words)>1:
                secondword=words[1]
            if len(words)>2:
                thirdword=words[1]
            auxusr={}
            auxusr['key']= firstword
            auxusr['value']= secondword
            auxusr['match']= 'general'
            auxusr['line']= line

            newmatcgeneral=[]
            oldmatchgeneral=sshdfact['generalsection'].copy()
            foundmg=False
            
            #print(existline)
            linenum=0
            for MG in sshdfact['generalsection']:
                #if MG['match']==existline['tag']:
                #    foundmg=True
                #print(MG['match']+" --- "+existline['tag'])
                #if (MG['match']==existline['tag'] and line.strip().upper() == MG['line'].strip().upper() and MG['key'].strip().upper()==firstword.strip().upper()):
                #    # ignore this line
                #    linenum=linenum+1
                #    print("line found: "+line)
                #else:
                #    newmatcgeneral.append(MG)
                if linenum!=existline['line']:
                    newmatcgeneral.append(MG)
                linenum=linenum+1
            sshdfact['generalsection']=newmatcgeneral
            #sshdfact['generalsection'].append(auxusr)
            #for mu in sshdfact['matchusers']:
            #    print(mu)
            #print("")
        else:
            #line isn't there
            resultcode['rc']=2
    else:
        #previous unstable
        resultcode['rc']=3    

    rcstdout=["INF: Line "+line+" removed  from general section successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Line "+line+" isn't at general section (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to remove a line "+line+" from general section got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def replacelinefromglobal(linesrc,linetar,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        #existline=existslineinglobal(linesrc,sshdfact['generalsection'])
        existline=existsstartlineinglobal(linesrc,sshdfact['generalsection'])
        if (existline['exists']==True):
            words=linesrc.strip().split()
            firstword=""
            secondword=""
            thirdword=""
            if len(words)>0:
                firstword=words[0]
            if len(words)>1:
                secondword=words[1]
            if len(words)>2:
                thirdword=words[1]
            auxusr={}
            auxusr['key']= firstword
            auxusr['value']= secondword
            auxusr['match']= 'general'
            auxusr['line']= linesrc

            newmatcgeneral=[]
            oldmatchgeneral=sshdfact['generalsection'].copy()
            foundmg=False
            
            #print(existline)
            linenum=0
            #print("MG")
            for MG in sshdfact['generalsection']:
                #print(MG)
                if linenum!=existline['line']:
                    newmatcgeneral.append(MG)
                else:
                    tarmg={}
                    tarmg['key']= ""
                    tarmg['value']= ""
                    tarmg['match']= "'general'"
                    tarmg['line']= linetar
                    wordstar=linetar.strip().split()
                    if len(wordstar)>0:
                        tarmg['key']=wordstar[0]
                    if len(wordstar)>1:
                        tarmg['value']=wordstar[1]

                    newmatcgeneral.append(tarmg)
                linenum=linenum+1
            sshdfact['generalsection']=newmatcgeneral
            #sshdfact['generalsection'].append(auxusr)
            #for mu in sshdfact['matchusers']:
            #    print(mu)
            #print("")
        else:
            #line isn't there
            resultcode['rc']=2
    else:
        #previous unstable
        resultcode['rc']=3    

    rcstdout=["INF: Line "+linesrc+" replaced in general section with "+linetar+" successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Line "+linesrc+" isn't at general section (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to remove a line "+linesrc+" from general section got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode


def replacelinefromsection(sectionentrie,sectionkey,sectionvalue,sectionmatch,linesrc,linetar,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        #print("sectionmatch: "+sectionmatch)
        existline=existsstartlineinsection(linesrc,sshdfact[sectionentrie],sectionkey,sectionvalue,sectionmatch)
        if (existline['exists']==True):
            words=linesrc.strip().split()
            firstword=""
            secondword=""
            thirdword=""
            if len(words)>0:
                firstword=words[0]
            if len(words)>1:
                secondword=words[1]
            if len(words)>2:
                thirdword=words[1]
            auxusr={}
            auxusr['key']= sectionkey
            auxusr['value']= sectionvalue
            auxusr['match']= sectionmatch
            auxusr['line']= linesrc
            if sectionmatch=='general':
                auxusr['key']= firstword
                auxusr['value']= secondword

            newmatch=[]
            oldmatch=sshdfact[sectionentrie].copy()
            foundmg=False
            
            #print(existline)
            linenum=0
            #print("MG")
            for MG in sshdfact[sectionentrie]:
                #print(MG)
                if linenum!=existline['line']:
                    newmatch.append(MG)
                else:
                    tarmg={}
                    tarmg['key']= ""
                    tarmg['value']= ""
                    tarmg['match']= sectionmatch
                    tarmg['line']= linetar
                    
                    if sectionmatch!='general':
                        tarmg['key']= sectionkey
                        tarmg['value']= sectionvalue

                    wordstar=linetar.strip().split()
                    if len(wordstar)>0:
                        tarmg['key']=wordstar[0]
                    if len(wordstar)>1:
                        tarmg['value']=wordstar[1]

                    newmatch.append(tarmg)
                linenum=linenum+1
            sshdfact[sectionentrie]=newmatch
        else:
            #line isn't there
            resultcode['rc']=2
    else:
        #previous unstable
        resultcode['rc']=3    

    rcstdout=["INF: Line '"+linesrc+"' replaced in '"+sectionmatch+"' with '"+linetar+"' successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Line '"+linesrc+"' isn't at "+sectionmatch+" section (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to replace the line '"+linesrc+"' from "+sectionmatch+" section got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode


def replacelinefromsectionstarting(sectionentrie,sectionkey,sectionvalue,sectionmatch,linestarting,linetar,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        existline=existsstartlineinsection(linestarting,sshdfact[sectionentrie],sectionkey,sectionvalue,sectionmatch)
        if (existline['exists']==True):
            words=linestarting.strip().split()
            firstword=""
            secondword=""
            thirdword=""
            if len(words)>0:
                firstword=words[0]
            if len(words)>1:
                secondword=words[1]
            if len(words)>2:
                thirdword=words[1]
            auxusr={}
            auxusr['key']= sectionkey
            auxusr['value']= sectionvalue
            auxusr['match']= sectionmatch
            auxusr['line']= linestarting
            if sectionmatch=='general':
                auxusr['key']= firstword
                auxusr['value']= secondword

            newmatch=[]
            oldmatch=sshdfact[sectionentrie].copy()
            foundmg=False
            
            #print(existline)
            linenum=0
            #print("MG")
            for MG in sshdfact[sectionentrie]:
                #print(MG)
                if linenum!=existline['line']:
                    newmatch.append(MG)
                else:
                    tarmg={}
                    tarmg['key']= ""
                    tarmg['value']= ""
                    tarmg['match']= sectionmatch
                    tarmg['line']= linetar
                    
                    if sectionmatch!='general':
                        tarmg['key']= sectionkey
                        tarmg['value']= sectionvalue

                    wordstar=linetar.strip().split()
                    if len(wordstar)>0:
                        tarmg['key']=wordstar[0]
                    if len(wordstar)>1:
                        tarmg['value']=wordstar[1]

                    newmatch.append(tarmg)
                linenum=linenum+1
            sshdfact[sectionentrie]=newmatch
        else:
            #line isn't there
            resultcode['rc']=2
    else:
        #previous unstable
        resultcode['rc']=3    

    rcstdout=["INF: Line starting with '"+linestarting+"' replaced in '"+sectionmatch+"' with '"+linetar+"' successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Line starting with '"+linestarting+"' isn't at "+sectionmatch+" section (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to replace a line starting with '"+linestarting+"' from "+sectionmatch+" section got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode


def addlinetomatchuser(line,user,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        exists=existsmatchuser(user,sshdfact,sshdlogdic)
        if exists['exists']==True:
            existline=existslineinsection(line,exists['tag'],sshdfact['matchusers'])
            if (existline['exists']==False):
                words=line.strip().split()
                firstword=""
                secondword=""
                if len(words)>0:
                    firstword=words[0]
                if len(words)>1:
                    secondword=words[1]
                auxusr={}
                auxusr['key']= firstword
                auxusr['value']= secondword
                auxusr['match']= exists['tag']
                auxusr['line']= line
                newmatchusers=[]
                oldmatchusers=sshdfact['matchusers'].copy()
                foundmu=False
                inserted=False
                pos=0
                for MU in oldmatchusers:
                    pos=pos+1
                    if MU['match']==exists['tag']:
                        foundmu=True
                    if MU['match']!=exists['tag']  and foundmu==True and inserted==False:
                        inserted=True
                        newmatchusers.append(auxusr)
                    newmatchusers.append(MU)
                    if pos==len(oldmatchusers) and foundmu==True and inserted==False:
                        inserted=True
                        newmatchusers.append(auxusr)
                        
                        
                sshdfact['matchusers']=newmatchusers
                #for mu in sshdfact['matchusers']:
                #    print(mu)
                #print("")
            else:
                #linealready there
                resultcode['rc']=3
        else:
            #matchuser isn't there
            resultcode['rc']=2
    else:
        #previous unstable
        resultcode['rc']=4

    rcstdout=["INF: Line added to Match user "+user+" successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "ERR: Match User "+user+" isn't there (rc=2).",
            "WAR: Line "+line+" already at Match user "+user+"  (rc=3).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=4).",
            "ERR: After trying to add a line "+line+" to Match user got unstable server sshd -t = "+RESCODE+" error (rc=5)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def addlinetomatchgroup(line,group,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''

    if sshdfact['stable']==0:
        exists=existsmatchgroup(group,sshdfact,sshdlogdic)
        if exists['exists']==True:
            existline=existslineinsection(line,exists['tag'],sshdfact['matchgroups'])
            if (existline['exists']==False):
                words=line.strip().split()
                firstword=""
                secondword=""
                if len(words)>0:
                    firstword=words[0]
                if len(words)>1:
                    secondword=words[1]
                auxusr={}
                auxusr['key']= firstword
                auxusr['value']= secondword
                auxusr['match']= exists['tag']
                auxusr['line']= line
                newmatchgroups=[]
                oldmatchgroups=sshdfact['matchgroups'].copy()
                foundmg=False
                inserted=False
                pos=0
                for MG in oldmatchgroups:
                    pos=pos+1
                    if MG['match']==exists['tag']:
                        foundmg=True
                    if MG['match']!=exists['tag']  and foundmg==True and inserted==False:
                        inserted=True
                        newmatchgroups.append(auxusr)
                    newmatchgroups.append(MG)
                    if pos==len(oldmatchgroups) and foundmg==True and inserted==False:
                        inserted=True
                        newmatchgroups.append(auxusr)

                sshdfact['matchgroups']=newmatchgroups
                #for mg in sshdfact['matchgroups']:
                #    print(mg)
                #print("")
            else:
                #linealready there
                resultcode['rc']=3
        else:
            #matchgroup isn't there
            resultcode['rc']=2
    else:
        #previous unstable
        resultcode['rc']=4
    rcstdout=["INF: Line added to Match group "+group+" successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "ERR: Match Group "+group+" isn't there (rc=2).",
            "WAR: Line "+line+" already at Match group "+group+"  (rc=3).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=4).",
            "ERR: After trying to add a line "+line+" to Match group got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode


def removelinefrommatchuser(line,user,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    linenum=0
    if sshdfact['stable']==0:
        exists=existsmatchuser(user,sshdfact,sshdlogdic)
        if exists['exists']==True:
            existline=existslineinsection(line,exists['tag'],sshdfact['matchusers'])
            if (existline['exists']==True):
                words=line.strip().split()
                firstword=""
                secondword=""
                if len(words)>0:
                    firstword=words[0]
                if len(words)>1:
                    secondword=words[1]
                newmatchusers=[]
                oldmatchusers=sshdfact['matchusers'].copy()
                foundmu=False
                for MU in oldmatchusers:
                    if MU['match']==exists['tag']:
                        foundmu=True
                    if (MU['match']==exists['tag'] and line.strip().upper() == MU['line'].strip().upper() and MU['key'].strip().upper()==firstword.strip().upper()):
                        # ignore this line
                        linenum=linenum+1
                    else:
                        newmatchusers.append(MU)

                sshdfact['matchusers']=newmatchusers
            else:
                #line isn't  there
                resultcode['rc']=3
        else:
            #matchuser isn't there
            resultcode['rc']=2
    else:
        #previous unstable
        resultcode['rc']=4


    rcstdout=["INF: Line removed from Match user "+user+" successfully ("+str(linenum)+" lines removed) (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Match user "+user+" isn't there (rc=2).",
            "ERR: Line "+line+" isn't at Match user "+user+"  (rc=3).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=4).",
            "ERR: After trying to remove a line "+line+" from Match user got unstable server sshd -t = "+RESCODE+" error (rc=5)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode

def removelinefrommatchgroup(line,group,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    linenum=0
    if sshdfact['stable']==0:
        exists=existsmatchgroup(group,sshdfact,sshdlogdic)
        if exists['exists']==True:
            existline=existslineinsection(line,exists['tag'],sshdfact['matchgroups'])
            if (existline['exists']==True):
                words=line.strip().split()
                firstword=""
                secondword=""
                if len(words)>0:
                    firstword=words[0]
                if len(words)>1:
                    secondword=words[1]
                newmatchgroups=[]
                oldmatchgroups=sshdfact['matchgroups'].copy()
                foundmu=False
                for MU in oldmatchgroups:
                    if MU['match']==exists['tag']:
                        foundmu=True
                    if (MU['match']==exists['tag'] and line.strip().upper() == MU['line'].strip().upper() and MU['key'].strip().upper()==firstword.strip().upper()):
                        # ignore this line
                        linenum=linenum+1
                    else:
                        newmatchgroups.append(MU)

                sshdfact['matchgroups']=newmatchgroups
            else:
                #line isn't  there
                resultcode['rc']=3
        else:
            #matchgroup isn't there
            resultcode['rc']=2
    else:
        #previous unstable
        resultcode['rc']=4


    rcstdout=["INF: Line removed from Match group "+group+" successfully ("+str(linenum)+" lines removed) (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Match group "+group+" isn't there (rc=2).",
            "ERR: Line "+line+" isn't at Match group "+group+"  (rc=3).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=4).",
            "ERR: After trying to remove a line "+line+" from Match group got unstable server sshd -t = "+RESCODE+" error (rc=5)."
            ]

    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode


def replacelinefrommatchgroup(linesrc,linetar,sshdfact,sshdlogdic):
    resultcode={}
    resultcode['rc']=0
    resultcode['stdout']=''
    RESCODE=''
    if sshdfact['stable']==0:
        existline=existsstartlineinglobal(linesrc,sshdfact['matchgroups'])
        if (existline['exists']==True):
            words=linesrc.strip().split()
            firstword=""
            secondword=""
            thirdword=""
            if len(words)>0:
                firstword=words[0]
            if len(words)>1:
                secondword=words[1]
            if len(words)>2:
                thirdword=words[1]
            auxusr={}
            auxusr['key']= firstword
            auxusr['value']= secondword
            auxusr['match']= 'general'
            auxusr['line']= linesrc

            newmatch=[]
            oldmatch=sshdfact['matchgroups'].copy()
            foundmg=False
            
            #print(existline)
            linenum=0
            #print("MG")
            for MG in sshdfact['matchgroups']:
                #print(MG)
                if linenum!=existline['line']:
                    newmatch.append(MG)
                else:
                    tarmg={}
                    tarmg['key']= ""
                    tarmg['value']= ""
                    tarmg['match']= 'matchgroups'
                    tarmg['line']= linetar
                    wordstar=linetar.strip().split()
                    if len(wordstar)>0:
                        tarmg['key']=wordstar[0]
                    if len(wordstar)>1:
                        tarmg['value']=wordstar[1]

                    newmatch.append(tarmg)
                linenum=linenum+1
            sshdfact['matchgroups']=newmatch
            #sshdfact['generalsection'].append(auxusr)
            #for mu in sshdfact['matchusers']:
            #    print(mu)
            #print("")
        else:
            #line isn't there
            resultcode['rc']=2
    else:
        #previous unstable
        resultcode['rc']=3    

    rcstdout=["INF: Line "+linesrc+" replaced in general section with "+linetar+" successfully (rc=0).",
            "ERR: sshd not installed (rc=1).",
            "WAR: Line "+linesrc+" isn't at matchgroup section (rc=2).",
            "ERR: Previous unstable server sshd -t = "+RESCODE+" error (rc=3).",
            "ERR: After trying to remove a line "+linesrc+" from general section got unstable server sshd -t = "+RESCODE+" error (rc=4)."
            ]
    resultcode['stdout']=rcstdout[resultcode['rc']]
    return resultcode
