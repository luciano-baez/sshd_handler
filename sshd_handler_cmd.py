# encoding: utf-8
## #!/usr/bin/python
#
# Copyright: (c) 2020, Luciano Baez <lucianobaez@kyndryl>
#                                   <lucianobaez1@ibm.com>
#                                   <lucianobaez@outlook.com>
#
# Latest version at https://github.kyndryl.net/lucianobaez
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#  This is a module to handle /etc/sudoers file
#
# History
#   -Ver 0.1 : Feb 26 2021
#           - Generate only report


import os
import sys
import datetime
# Importing all functions from repo lib sudo_handler_lib

from sshd_handler_lib import getsshd_fact 
from sshd_handler_lib import validatesshd
from sshd_handler_lib import existsmatchuser
from sshd_handler_lib import existsmatchgroup
from sshd_handler_lib import addmatchuser
from sshd_handler_lib import addmatchuserfirst
from sshd_handler_lib import removematchuser
from sshd_handler_lib import addmatchgroup
from sshd_handler_lib import addmatchgroupfirst
from sshd_handler_lib import removematchgroup

from sshd_handler_lib import addlinetoglobal
from sshd_handler_lib import removelinefromglobal
from sshd_handler_lib import replacelinefromglobal

from sshd_handler_lib import addlinetomatchuser
from sshd_handler_lib import addlinetomatchgroup
from sshd_handler_lib import removelinefrommatchuser
from sshd_handler_lib import removelinefrommatchgroup

from sshd_handler_lib import savesshd_config

from sshd_handler_lib import restartsshd


# Variable Definition
#------------------------------------------------------------------------------------------------------------
# LogHandling
logdic = dict(
    log=False,
    logfile="/var/log/sshd_handler"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".log"
    )

sshd_fact={}
sshd_handlercfg = dict(
    version="0.1",
    process=True,
    report=False,
    restart=False,
    cmdusage=False,
    backup=True,
    validate=False,
    savefiles=False
    )

scriptname="sshd_handler_cmd"

#List of users to process
sshd_module_addusers=[]
sshd_module_addusersfirst=[]
sshd_module_removeusers=[]
sshd_module_addgroups=[]
sshd_module_addgroupsfirst=[]
sshd_module_removegroups=[]

sshd_module_globaladddir=[]
sshd_module_globalremovedir=[]
sshd_module_globalreplacedirsrc=[]
sshd_module_globalreplacedirtar=[]
sshd_module_umadddir=[]
sshd_module_umremovedir=[]
sshd_module_gmadddir=[]
sshd_module_gmremovedir=[]
sshd_module_backup=False

#List of unknown arguments
sshd_module_argumentsnotdetected=[]

def cmduse():
    print ("Command usage: ")
    print ("  -? or -h                              : Provides this output.")
    print ("  -report                               : Provides a report without any change .")
    print ("  -validate                             : Validate sshd server config. ")
    print ("  -restart                              : Restart sshd service if sshd_config is valid. ")
    print ("  -addmatchuser=USER                    : Add a Match User section for user USER.")
    print ("  -addmatchuserfirst=USER               : Add a Match User section for user USER at the begining.")
    print ("  -removematchuser=USER                 : Remove a Match User section of user USER and all directives")
    print ("                                            applied to this Math User.")
    print ("  -addmatchgroup=GROUP                  : Add a Match Group section for group GROUP.")
    print ("  -addmatchgroupfirst=GROUP             : Add a Match Group section for group GROUP at the begining.")
    print ("  -removematchgroup=GROUP               : Remove a Match Group section of user GROUP and all directives")
    print ("                                            applied to this Math Group.")
    print ("  -adddirgeneral=DIRECTIVE              : Add a Directive (DIRECTIVE is a text line in between \"\") ")
    print ("                                            to the general section (applies to all users and groups).")
    print ("  -removedirgeneral=DIRECTIVE           : Removes a Directive (DIRECTIVE is a text line in between \"\") ")
    print ("                                            from the general section (applies to all users and groups).")
    print ("  -replacedirgeneral=DIRSTART,DIRECTIVE : Replaces a Directive that starts with DIRSTART with the direcvie DIRECTIVE")
    print ("                                            (DIRECTIVE is a text line in between \"\") ")
    print ("                                            from the general section (applies to all users and groups).")

    print ("  -adddirtomatchusr=USER,DIRECTIVE      : Add a Directive (DIRECTIVE is a text line in between \"\") ")
    print ("                                            to the specific Match User USER.")
    print ("  -removedirfrommatchusr=USER,DIRECTIVE : Remove a Directive (DIRECTIVE is a text line in between \"\") ")
    print ("                                            from the specific Match User USER.")
    print ("  -adddirtomatchgrp=GROUP,DIRECTIVE     : Add a Directive (DIRECTIVE is a text line in between \"\") ")
    print ("                                            to the specific Match group GROUP.")
    print ("  -removedirfrommatchgrp=GROUP,DIRECTIVE: Remove a Directive (DIRECTIVE is a text line in between \"\") ")
    print ("                                            from the specific Match User USER.")
    print ("")
    print ("Example: (adding a Match Group section ) ")
    print (" sshd_handler_cmd -addmatchgroup=ahadm ")
    print ("Example: (adding 2 directives to the previous deffined Match Group section ) ")
    print (" sshd_handler_cmd  -adddirtomatchgrp=ahadm,\"AuthenticationMethods publickey\" -adddirtomatchgrp=ahadm,\"PubkeyAuthentication yes\"")
    print ("")


# Processs Arguments
#------------------------------------------------------------------------------------------------------------
# Count the arguments
arguments = len(sys.argv) - 1
# Output argument-wise
position = 1
insuficientarguments=False
if arguments == 0:
    # Print cmd usage
    cmdusage=1

if arguments==0:
    sshd_handlercfg['cmdusage']=True
print (scriptname+" Ver:"+sshd_handlercfg['version']+" ")
paramargs=[]
paramargs.append("")
paramargs.append("")
paramargs.append("")
paramargs.append("")
while (arguments >= position):
    argunknown=True
    arg=sys.argv[position]
    #print ("Parameter %i: %s" % (position, arg))
    argcomponents=arg.strip().split('=')
    directive=argcomponents[0]
    if len(argcomponents)>1:
        directiveargs=argcomponents[1].strip().split(',')
    else:
        aux=",,"
        directiveargs=aux.strip().split(',')


    # Hadling Help
    if directive == "-h":
        sshd_handlercfg['cmdusage']=True
        argunknown=False
    if directive == "-?":
        sshd_handlercfg['cmdusage']=True
        argunknown=False
    if directive == "-report":
        sshd_handlercfg['report']=True
        argunknown=False
    if directive == "-r":
        sshd_handlercfg['report']=True
        argunknown=False

    if directive == "-restart":
        sshd_handlercfg['restart']=True
        argunknown=False

    if directive == "-validate":
        sshd_handlercfg['validate']=True
        argunknown=False

    if directive == "-addmatchuser":
        sshd_module_addusers.append(argcomponents[1])
        argunknown=False
    
    if directive == "-addmatchuserfirst":
        sshd_module_addusersfirst.append(argcomponents[1])
        argunknown=False

    if directive == "-removematchuser":
        sshd_module_removeusers.append(argcomponents[1])
        argunknown=False

    if directive == "-addmatchgroup":
        sshd_module_addgroups.append(argcomponents[1])
        argunknown=False
    
    if directive == "-addmatchgroupfirst":
        sshd_module_addgroupsfirst.append(argcomponents[1])
        argunknown=False

    if directive == "-removematchgroup":
        sshd_module_removegroups.append(argcomponents[1])
        argunknown=False

    if directive == "-adddirgeneral":
        sshd_module_globaladddir.append(argcomponents[1])
        argunknown=False
    
    if directive == "-removedirgeneral":
        sshd_module_globalremovedir.append(argcomponents[1])
        argunknown=False

    if directive == "-replacedirgeneral":
        #sshd_module_globalremovedir.append(argcomponents[1])
        argparts=argcomponents[1].strip().split(',')
        dirsrc=""
        dirtar=""
        if len(argparts)>0:
            dirsrc=argparts[0]
        if len(argparts)>1:
            dirtar=argparts[1]
        sshd_module_globalreplacedirsrc.append(dirsrc)
        sshd_module_globalreplacedirtar.append(dirtar)
        argunknown=False
        print("-replacedirgeneral "+dirsrc+" con "+dirtar)

    if directive == "-adddirtomatchusr":
        mudirective={}
        mudirective['user']=directiveargs[0]
        mudirective['directive']=directiveargs[1]
        print(mudirective)
        sshd_module_umadddir.append(mudirective)
        argunknown=False
    
    if directive == "-removedirfrommatchusr":
        mudirective={}
        mudirective['user']=directiveargs[0]
        mudirective['directive']=directiveargs[1]
        sshd_module_umremovedir.append(mudirective)
        argunknown=False

    if directive == "-adddirtomatchgrp":
        mgdirective={}
        mgdirective['group']=directiveargs[0]
        mgdirective['directive']=directiveargs[1]
        sshd_module_gmadddir.append(mgdirective)
        argunknown=False
    
    if directive == "-removedirfrommatchgrp":
        mgdirective={}
        mgdirective['group']=directiveargs[0]
        mgdirective['directive']=directiveargs[1]
        sshd_module_gmremovedir.append(mgdirective)
        argunknown=False


    #Process unknown arguments
    if argunknown == True:
        sshd_module_argumentsnotdetected.append(directive)
    position = position + 1



# Processing Detected Arguments
#------------------------------------------------------------------------------------------------------------
if sshd_handlercfg['process']==True:
    #Getting sshd Facts
    sshd_fact=getsshd_fact (logdic)
    # Detect if have sudo
    if sshd_fact['installed']== True:
        print("INF: sshd_handler on "+sshd_fact['server']+" ("+sshd_fact['platform']+").")
        if (len(sshd_module_argumentsnotdetected)==0) :
            globalerror=0
            #Processing arguments without errors
            
            # Adding Match user section to the cfg files
            for user in sshd_module_addusers:
                sshd_handlercfg['savefiles']= True
                print("INF: Adding Match user "+user+" to sshd cfg.")
                RC=addmatchuser(user,sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])
    
            # Adding Match user section at the begining to the cfg files
            for user in sshd_module_addusersfirst:
                sshd_handlercfg['savefiles']= True
                print("INF: Adding Match user "+user+" to sshd cfg at the begining.")
                RC=addmatchuserfirst(user,sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])

            # Removing Match user section from the cfg files
            for user in sshd_module_removeusers:
                sshd_handlercfg['savefiles']= True
                print("INF: Removing Match user "+user+" from sshd cfg.")
                RC=removematchuser(user,sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])

            # Adding Match Group section to the cfg files
            for group in sshd_module_addgroups:
                sshd_handlercfg['savefiles']= True
                print("INF: Adding Match group "+group+" to sshd cfg.")
                RC=addmatchgroup(group,sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])
  
            # Adding Match Group section at the begining to the cfg files
            for group in sshd_module_addgroupsfirst:
                sshd_handlercfg['savefiles']= True
                print("INF: Adding Match group "+group+" to sshd cfg at the begining.")
                RC=addmatchgroupfirst(group,sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])

            # Removing Match Groups from the cfg files
            for group in sshd_module_removegroups:
                sshd_handlercfg['savefiles']= True
                print("INF: Removing Match group "+group+" from sshd cfg.")
                RC=removematchgroup(group,sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])            

            #Adding Lines to global section
            for directive in sshd_module_globaladddir:
                sshd_handlercfg['savefiles']= True
                print("INF: Adding Line \""+directive+"\" to global section.")
                RC=addlinetoglobal(directive,sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])

            #Removing Lines from global section
            for directive in sshd_module_globalremovedir:
                sshd_handlercfg['savefiles']= True
                print("INF: Removing Line \""+directive+"\" form global section.")
                RC=removelinefromglobal(directive,sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])

            #Changing Lines from global section
            posdir=0
            for directive in sshd_module_globalreplacedirsrc:
                replacedir=sshd_module_globalreplacedirtar[posdir]
                sshd_handlercfg['savefiles']= True
                print("INF: replacing Line \""+directive+"\" form global section with "+replacedir+".")
                RC=replacelinefromglobal(directive,replacedir,sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])
                posdir=posdir+1


            #Adding Lines to Match user section
            for directive in sshd_module_umadddir:
                sshd_handlercfg['savefiles']= True
                print("INF: Adding Line \""+directive['directive']+"\" from Match user \""+directive['user']+"\" section.")
                RC=addlinetomatchuser(directive['directive'],directive['user'],sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])

            #Removing Lines from Match user section
            for directive in sshd_module_umremovedir:
                sshd_handlercfg['savefiles']= True
                print("INF: Removing Line \""+directive['directive']+"\" from Match user \""+directive['user']+"\" section.")
                RC=removelinefrommatchuser(directive['directive'],directive['user'],sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])

            #Adding Lines to Match Group section
            for directive in sshd_module_gmadddir:
                sshd_handlercfg['savefiles']= True
                print("INF: Adding Line \""+directive['directive']+"\" from Match group \""+directive['group']+"\" section.")
                RC=addlinetomatchgroup(directive['directive'],directive['group'],sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])

            #Removing Lines from Match Group section
            for directive in sshd_module_gmremovedir:
                sshd_handlercfg['savefiles']= True
                print("INF: Removing Line \""+directive['directive']+"\" from Match group \""+directive['group']+"\" section.")
                RC=removelinefrommatchgroup(directive['directive'],directive['group'],sshd_fact,logdic)
                if RC['rc']>0:
                    globalerror=globalerror+1
                print(RC['stdout'])


            # Printing report
            if sshd_handlercfg['report']== True:
                if (sshd_fact['installed']==True):
                    
                    print("INF: SSHD installed on platform "+sshd_fact['platform']+" Ver.: "+sshd_fact['version'])
                    sshdstate=""
                    if sshd_fact['stable'] == 0:
                        sshdstate="stable"
                    else: 
                        sshdstate="unstable"
                    print("INF: State: "+sshdstate+" resultcode:"+str(sshd_fact['stable']))
                    print("INF: bin: "+sshd_fact['binfile']+"  CFG file:"+sshd_fact['cfgfie'])
                    print("")
                    print("INF: General section: ")
                    for line in sshd_fact['generalsection']:
                        print(line)
                    #print(sshd_fact['generalsection'])

                    print("")
                    print("INF: Match Users section: ")
                    for line in sshd_fact['matchusers']:
                        print(line)
                    #print(sshd_fact['matchusers'])

                    print("")
                    print("INF: Match Groups section: ")
                    for line in sshd_fact['matchgroups']:
                        print(line)
                    #print(sshd_fact['matchgroups'])
                    print("")
                    
                else:
                    print("ERR: SSHD NOT installed or not detected. ")
                
            # Save configuration
            if (sshd_handlercfg['savefiles']==True):
                if (globalerror==0):
                    #RC=savesshd_config(sshd_fact,logdic)
                    RC=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    print(RC['stdout'])
                else:
                    print("ERR: cfg file could not be saved due error(s) ("+str(globalerror)+")")
                    
                    
            #Validate 
            if sshd_handlercfg['validate']== True:
                result=validatesshd(sshd_fact['platform'],logdic)
                if result ==0:
                    print("INF: SSHD config stable.")
                else:
                    print("ERR: SSHD config unstable.")
            
            #Restart the service 
            if sshd_handlercfg['restart']== True:
                result=validatesshd(sshd_fact['platform'],logdic)
                if result ==0:
                    print("INF: Restarting the sshd service.")
                    restartsshd(sshd_fact['platform'],logdic)
                else:
                    print("ERR: Couldn't restart the service, the SSHD config is unstable.")

        else:
            # Error Handling
            if (len(sshd_module_argumentsnotdetected)>0):
                print("ERR: Argument Error.")

            sshd_handlercfg['cmdusage'] = True
            print('')
            #Processing unknwon arguments
            for uargu in sshd_module_argumentsnotdetected:
                print("ERR: Argument "+uargu+" not recognized.")
            print('')

    else:
        print("ERR: sshd not installed")    
#Handling Help
if sshd_handlercfg['cmdusage'] == True:
    cmduse()
#print(existsmatchuser('pepe2',sshd_fact,logdic))



#------------------------------------------------------------------------------------------------------------
