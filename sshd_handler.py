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

ANSIBLE_METADATA = {
    'metadata_version': '0.8',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: sshd_handler

short_description: Module to handle sshd  (/etc/ssh/sshd_config) in Kyndryl/IBM under Unix/linux platforms

version_added: "0.1"

description:
    - "This is module provides sshd handle"

extends_documentation_fragment:
    - To be executed on Jump Host and Ansible TOWER

author:
    - Luciano Báez (@lucianoabez) on Kyndryl slack and on IBM slack (@lucianoabez1)
'''

EXAMPLES = '''
Get who to use it from

'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
    returned: always
message:
    description: The output message that the SUDO module generates
    type: str
    returned: always
'''

import os
import pwd
import grp
import platform
import subprocess
import json
import shutil
import datetime

# Importing all functions from repo lib sudo_handler_lib
from ansible.module_utils.sshd_handler_lib import *

#Needed to be usable as Ansible Module
from ansible.module_utils.basic import AnsibleModule



def sudoershandle(options):
    SUDOHANDLERESULT={}
    return SUDOHANDLERESULT
    

def run_module():
    #------------------------------------------------------------------------------------------------------------
    # This are the arguments/parameters that a user can pass to this module
    # the action is the only one that is required



    module_args = dict(
        #action=dict(type='str', required=True),
        state=dict(type='str', default='present'),
        section=dict(type='str', required=False),
        directive=dict(type='str', required=False, default=""),
        first=dict(type='bool', required=False, default=False),
        #newdirective=dict(type='bool', required=False, default=False),
        newdirective=dict(type='str', required=False, default=""),
        directivestarting=dict(type='str', required=False, default=""),
        matchgroup=dict(type='str', required=False, default=""),
        matchuser=dict(type='str', required=False, default=""),
        backup=dict(type='bool', required=False, default=False),

        # Non documented option For troubleshoot
        log=dict(type='bool', required=False, default=False)
    )
    

    #------------------------------------------------------------------------------------------------------------
    # This is the dictionary to handle the module result
    result = dict(
        changed=False,
        failed=False,
        skipped=False,
        original_message='',
        message=''
    )

    # This is the dictionary to handle the logs
    logdic = dict(
        log=False,
        logfile='/tmp/sudo_handler'
    )

    # The AnsibleModule object will be our abstraction working with Ansible this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module supports check mode
    
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # Define Vaariables to use 
    sshd_process=1
    sshd_file=str('/etc/ssh/sshd_config')
    sshd_module_first=False
    sshd_module_log=False
    sshd_module_state=str('')
    sshd_module_section=str('')
    sshd_module_directive=str('')
    sshd_module_newdirective=str('')
    sshd_module_directivestarting=str('')
    sshd_module_matchgroup=str('')
    sshd_module_matchuser=str('')
    sshd_module_backup=False
    sshd_module_validate=False
    sshd_module_restart=False
    #


    # Provide the the requested action as the original Message
    CR="\n"
    result['original_message'] = module.params
    #result['message'] = 'goodbye',
    ModuleExitMessage = ''
    ModuleExitChanged = False
    ModuleExitFailed= False

    # <processing parameters>
    try:
        sshd_module_state=str(module.params['state'])
    except KeyError:
        sshd_module_state='present'

    if sshd_module_state != 'report':
        #Process when state is present or absent
        if sshd_module_state == 'present' or sshd_module_state == 'absent' or sshd_module_state == 'replace':
            # Detects if fixincludedir in order to remove '#includedir' directive
            try:
                sshd_module_section=module.params['section']
            except:
                sshd_module_section=str('')
            try:
                sshd_module_directive=module.params['directive']
            except:
                sshd_module_directive=str('')
            
            try:
                sshd_module_first=module.params['first']
            except:
                sshd_module_first=False

            try:
                sshd_module_backup=module.params['backup']
            except:
                sshd_module_backup=False

            try:
                sshd_module_newdirective=module.params['newdirective']
            except:
                sshd_module_newdirective=str('')
            try:
                sshd_module_directivestarting=module.params['directivestarting']
            except:
                sshd_module_directivestarting=str('')
            try:
                sshd_module_matchgroup=module.params['matchgroup']
            except:
                sshd_module_matchgroup=str('')
            try:
                sshd_module_matchuser=module.params['matchuser']
            except:
                sshd_module_matchuser=str('')
        if sshd_module_state == 'validate':
            sshd_module_validate=True
        if sshd_module_state == 'restart':
            sshd_module_restart=True
            
        # Processing non reporting actions
        if ( os.path.isfile(sshd_file) == False):
            sshd_process=0
            ModuleExitMessage = ModuleExitMessage + "sshd_conifg file not present." + CR   
        
        if sshd_module_section != '':
            if sshd_module_state == 'replace' and sshd_module_directive != '':
                if  sshd_module_newdirective == '' and sshd_module_directivestarting == '':
                    sshd_process=0
                    ModuleExitMessage = ModuleExitMessage + "To replace "+sshd_module_directive+" you must provide newdirective or directivestarting." + CR  
                if  sshd_module_newdirective != '' and sshd_module_directivestarting != '':
                    sshd_process=0
                    ModuleExitMessage = ModuleExitMessage + "To replace "+sshd_module_directive+" you must provide newdirective or directivestarting exclusively, not both." + CR  

            if sshd_module_section != 'general' and sshd_module_section != 'matchgroup' and sshd_module_section != 'matchuser':
                sshd_process=0
                ModuleExitMessage = ModuleExitMessage + "Section "+sshd_module_section+" not recognized." + CR   

            elif sshd_module_section == 'general':
                if sshd_module_directive == '' and sshd_module_directivestarting=='':
                    sshd_process=0
                    ModuleExitMessage = ModuleExitMessage + "Section "+sshd_module_section+" must have a directive to place or remove." + CR   

            elif sshd_module_section == 'matchuser':            
                if sshd_module_matchuser == '':
                    sshd_process=0
                    ModuleExitMessage = ModuleExitMessage + "A matchuser should be provided when you use Section "+sshd_module_section+"." + CR

            elif sshd_module_section == 'matchgroup':
                if sshd_module_matchgroup == '':
                    sshd_process=0
                    ModuleExitMessage = ModuleExitMessage + "A matchgroup should be provided when you use Section "+sshd_module_section+"." + CR
        else: 
            if sshd_module_state != 'validate' and sshd_module_state != 'restart':
                sshd_process=0
                ModuleExitMessage = ModuleExitMessage + "State "+sshd_module_state+" not recognized." + CR   

    # </processing parameters>

    # <Call Library Functions>
    if sshd_process==1:
        # Getting sudo fats
        sshd_fact=getsshd_fact(logdic)

        #Processing the report
        if sshd_module_state == 'report':
            result['changed']=False
            if len(sshd_fact) > 0:
                #result['message']=sshd_fact
                ModuleExitMessage=sshd_fact
            else:
                result['failed'] = True
                ModuleExitMessage="No sshd config detected."
                #result['message']="No sshd config detected."
        elif sshd_module_state == 'restart':
            rc=restartsshd(sshd_fact['platform'],logdic)
            if rc['rc'] == 0:
                result['changed'] = True
            else:
                result['changed'] = False
                result['failed'] = True
            ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR
        elif sshd_module_state == 'validate':
            rcnum=validatesshd(sshd_fact['platform'],logdic)
            if rcnum == 0:
                result['changed'] = True
            else:
                result['changed'] = False
                result['failed'] = True
            ModuleExitMessage = ModuleExitMessage + "Validate action with rc="+str(rcnum)+"." + CR

        #Present state
        elif sshd_module_state == 'present':
            # Code section to add or place infotmation to sshd_config
            if sshd_module_section == 'general' and sshd_module_directive != '':
                if sshd_module_first==True:
                    #rc=addlinetoglobalfirst(sshd_module_directive,sshd_fact,logdic)
                    rc=addlinetoglobalat(0,sshd_module_directive,sshd_fact,logdic)
                else:
                    rc=addlinetoglobal(sshd_module_directive,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        result['failed'] = True
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                else:
                    result['changed'] = False
                    result['failed'] = True
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR

            if sshd_module_section == 'matchgroup' and sshd_module_matchgroup != '':
                if sshd_module_first==True:
                    # make sure that is at the begining
                    rc=addmatchgroupfirst(sshd_module_matchgroup,sshd_fact,logdic)
                else:
                    # make sure that is there anywhere
                    rc=addmatchgroup(sshd_module_matchgroup,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        result['failed'] = True
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                else:
                    result['changed'] = False
                    result['failed'] = True
                    if rc['rc'] == 2:
                        result['failed'] = False
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR
                if result['failed'] == False and  sshd_module_directive != '':
                    # make sure that the directive is at the matchgourp
                    ModuleExitMessage =ModuleExitMessage + json.dumps(sshd_fact)
                    rc=addlinetomatchgroup(sshd_module_directive,sshd_module_matchgroup,sshd_fact,logdic)
                    if rc['rc'] == 0:
                        result['changed'] = True
                        rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                        if rcsave['rc'] > 0:
                            result['changed'] = False
                            result['failed'] = True
                            ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                    else:
                        result['changed'] = False
                        result['failed'] = True
                        if rc['rc'] == 3:
                            result['failed'] = False
                    ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR

            if sshd_module_section == 'matchuser' and sshd_module_matchuser != '':
                if sshd_module_first==True:
                    # make sure that is at the begining
                    rc=addmatchuserfirst(sshd_module_matchuser,sshd_fact,logdic)
                else:
                    # make sure that is there anywhere
                    rc=addmatchuser(sshd_module_matchuser,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        result['failed'] = True
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                else:
                    result['changed'] = False
                    result['failed'] = True
                    if rc['rc'] == 2:
                        result['failed'] = False
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR
                if result['failed'] == False and  sshd_module_directive != '':
                    # make sure that the directive is at the matchuser
                    rc=addlinetomatchuser(sshd_module_directive,sshd_module_matchuser,sshd_fact,logdic)
                    if rc['rc'] == 0:
                        result['changed'] = True
                        rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                        if rcsave['rc'] > 0:
                            result['changed'] = False
                            result['failed'] = True
                            ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                    else:
                        result['changed'] = False
                        result['failed'] = True
                        if rc['rc'] == 3:
                            result['failed'] = False
                    ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR

        #absent state
        elif sshd_module_state == 'absent':
            # Code section to add or place infotmation to sshd_config
            if sshd_module_section == 'general' and sshd_module_directive != '':
                rc=removelinefromglobal(sshd_module_directive,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        result['failed'] = True
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                else:
                    result['changed'] = False
                    result['failed'] = True
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR

            if sshd_module_section == 'matchgroup' and sshd_module_matchgroup != '':
                if sshd_module_directive != '':
                    # Removing line from matchgroup
                    rc=removelinefrommatchgroup(sshd_module_directive,sshd_module_matchgroup,sshd_fact,logdic)
                else:
                    # Removing the matchgroup
                    rc=removematchgroup(sshd_module_matchgroup,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        result['failed'] = True
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                else:
                    result['changed'] = False
                    result['failed'] = True
                    if rc['rc'] == 2:
                            result['failed'] = False
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR
            
            if sshd_module_section == 'matchuser' and sshd_module_matchuser != '':
                if sshd_module_directive != '':
                    # Removing line from matchuser
                    rc=removelinefrommatchuser(sshd_module_directive,sshd_module_matchuser,sshd_fact,logdic)
                else:
                    # Removing the matchuser
                    rc=removematchuser(sshd_module_matchuser,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        result['failed'] = True
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                else:
                    result['changed'] = False
                    result['failed'] = True
                    if rc['rc'] == 2:
                            result['failed'] = False
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR

        # replace state
        elif sshd_module_state == 'replace':
            # Code section to replace infotmation on the general section
            if sshd_module_section == 'general' and sshd_module_directive != '' and sshd_module_newdirective != '' and sshd_module_directivestarting == '':
                # Replace  directive in general section 
                #rc=replacelinefromglobal(linesrc,linetar,sshdfact,sshdlogdic):
                #rc=replacelinefromglobal(sshd_module_directive,sshd_module_newdirective,sshd_fact,logdic)
                rc=replacelinefromsection('generalsection','','','general',sshd_module_directive,sshd_module_newdirective,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                        if rcsave['rc'] != 5:
                            result['failed'] = True
                else:
                    result['changed'] = False
                    result['failed'] = True
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR

            if sshd_module_section == 'general' and sshd_module_directive == '' and sshd_module_newdirective != '' and sshd_module_directivestarting != '':
                # Replace  directive in general section starting with a string
                rc=replacelinefromsectionstarting('generalsection','','','general',sshd_module_directivestarting,sshd_module_newdirective,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                        if rcsave['rc'] != 5:
                            result['failed'] = True
                else:
                    if rc['rc'] == 2:
                        #add if not present to replace
                        rc=addlinetoglobal(sshd_module_newdirective,sshd_fact,logdic)
                        if rc['rc'] == 0:
                            result['changed'] = True
                            rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                            if rcsave['rc'] > 0:
                                result['changed'] = False
                                ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                                if rcsave['rc'] != 5:
                                    result['failed'] = True
                    else:
                        result['changed'] = False
                        result['failed'] = True
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR


            if sshd_module_section == 'matchgroup' and sshd_module_matchgroup != ''  and sshd_module_directive != '' and sshd_module_newdirective != '' and sshd_module_directivestarting == '':
                # Replace a directive in a matchgroup
                rc=replacelinefromsection('matchgroups','','',sshd_module_matchgroup,sshd_module_directive,sshd_module_newdirective,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                        if rcsave['rc'] != 5:
                            result['failed'] = True
                else:
                    result['changed'] = False
                    result['failed'] = True
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR

            if sshd_module_section == 'matchgroup' and sshd_module_matchgroup != ''  and sshd_module_directive == '' and sshd_module_newdirective != '' and sshd_module_directivestarting != '':
                #rc=replacelinefromsection('matchgroups','','',sshd_module_matchgroup,sshd_module_directivestarting,sshd_module_newdirective,sshd_fact,logdic)
                rc=replacelinefromsectionstarting('matchgroups','','',sshd_module_matchgroup,sshd_module_directivestarting,sshd_module_newdirective,sshd_fact,logdic)
                
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                        if rcsave['rc'] != 5:
                            result['failed'] = True
                else:
                    if rc['rc'] == 2:
                        #add if not present to replace
                        rc=addlinetomatchgroup(sshd_module_newdirective,sshd_module_matchgroup,sshd_fact,logdic)
                        if rc['rc'] == 0:
                            result['changed'] = True
                            rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                            if rcsave['rc'] > 0:
                                result['changed'] = False
                                ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                                if rcsave['rc'] != 5:
                                    result['failed'] = True
                    else:
                        result['changed'] = False
                        result['failed'] = True
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR

            if sshd_module_section == 'matchuser' and sshd_module_matchuser != ''  and sshd_module_directive != '' and sshd_module_newdirective != '' and sshd_module_directivestarting == '':
                # Replace a directive in a matchuser
                rc=replacelinefromsection('matchusers','','',sshd_module_matchuser,sshd_module_directive,sshd_module_newdirective,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                        if rcsave['rc'] != 5:
                            result['failed'] = True
                else:
                    result['changed'] = False
                    result['failed'] = True
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR

            if sshd_module_section == 'matchuser' and sshd_module_matchuser != ''  and sshd_module_directive == '' and sshd_module_newdirective != '' and sshd_module_directivestarting != '':
                # Replace a directive in a matchuser starting with a string
                #rc=replacelinefromsection('matchusers','','',sshd_module_matchuser,sshd_module_directivestarting,sshd_module_newdirective,sshd_fact,logdic)
                #rc=replacelinefromsectionstarting('matchusers','','','matchuser',sshd_module_directivestarting,sshd_module_newdirective,sshd_fact,logdic)
                rc=replacelinefromsectionstarting('matchusers','','',sshd_module_matchuser,sshd_module_directivestarting,sshd_module_newdirective,sshd_fact,logdic)
                if rc['rc'] == 0:
                    result['changed'] = True
                    rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                    if rcsave['rc'] > 0:
                        result['changed'] = False
                        ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                        if rcsave['rc'] != 5:
                            result['failed'] = True
                else:
                    if rc['rc'] == 2:
                        #add if not present to replace
                        rc=addlinetomatchuser(sshd_module_newdirective,sshd_module_matchuser,sshd_fact,logdic)
                        if rc['rc'] == 0:
                            result['changed'] = True
                            rcsave=savesshd_config(sshd_module_backup,sshd_fact,logdic)
                            if rcsave['rc'] > 0:
                                result['changed'] = False
                                ModuleExitMessage = ModuleExitMessage + rcsave['stdout'] + CR
                                if rcsave['rc'] != 5:
                                    result['failed'] = True
                    else:
                        result['changed'] = False
                        result['failed'] = True
                ModuleExitMessage = ModuleExitMessage + rc['stdout'] + CR


        # End of declarative state parsing
        #---------------------------------------------------------------------------------------------------------------------------
    # </Call Library Functions>


    result['message'] = ModuleExitMessage
    # Returning the result
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()