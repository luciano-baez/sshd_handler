SSHD Handler  (Ver 0.8 ) (cmd script and Ansible module)
=========================================================
* This is a python script to be called from your shell script and a python module to be added in your playbooks or Roles in Ansible Tower*


## Requirements
------------
- For scripting python3
- For use in your playbooks in ansile, just usual Ansible requirements.

sshd_handler module
===================
* This is a python module to handle sshd configuration files and its includes
To implement this in a playbook you need to place the file sshd_handler.py in the "library" directory and the sshd_handler_lib.py on "module_utils" directory.


Module Functions
----------------
*Current programmed functions.*

Example get report
 
```yaml
  - name: sshd get report
    sshd_handler:
        state: report
```

Validate the /etc/ssh/sshd_config
```yaml
  - name: Validate the /etc/ssh/sshd_config
    sshd_handler:
        state: validate
```

Restart the sshd service
```yaml
  - name: Restart the sshd service
    sshd_handler:
        state: restart
```

**Handle Directives in sections**

Place a directive in a general section
```yaml
  - name: Place a directive in a general section
    sshd_handler:
        section: general
        directive: "PermitRootLogin yes"
        state: present
```

Place a directive in a match group section
```yaml
  - name: Add "PubkeyAuthentication yes" to access hub group  ahadm
    sshd_handler:
        section: matchgroup
        matchgroup: ahadm
        directive: "PubkeyAuthentication yes"
        state: present
```

Place a directive in a match group section a the begining 
```yaml
  - name: Add "PubkeyAuthentication yes" to access hub group  ahadm
    sshd_handler:
        section: matchgroup
        matchgroup: ahadm
        directive: "PubkeyAuthentication yes"
        first: true
        state: present
```

Place a directive in a match user section
```yaml
  - name: Add "PubkeyAuthentication yes" to a user ar007310
    sshd_handler:
        section: matchuser
        matchuser: ar007310
        directive: "PubkeyAuthentication yes"
        state: present
```

Make sure the directive is not present in a general section
```yaml
  - name: Make sure the directive is not present in a general section
    sshd_handler:
        section: general
        directive: "PermitRootLogin yes"
        state: absent
```

Make sure the directive is not present on a match group section
```yaml
  - name: Remove "PubkeyAuthentication yes" access hub group  ahadm
    sshd_handler:
        section: matchgroup
        matchgroup: ahadm
        directive: "PubkeyAuthentication yes"
        state: absent
```

Make sure the directive is not present on a match user section
```yaml
  - name: Remove "PubkeyAuthentication yes" from match user ar007310
    sshd_handler:
        section: matchuser
        matchuser: ar007310
        directive: "PubkeyAuthentication yes"
        state: absent
```

**Handle directives replacement**

Replace a directive in a general section
```yaml


```

Replace a directive starting with PermitRootLogin in a general section
```yaml
  - name: Replace the directive in a general section
    sshd_handler:
        section: general
        directivestarting: "PermitRootLogin"
        newdirective: "PermitRootLogin no"
        state: replace
```

**Handle sections**

Place a match group section
```yaml
  - name: Make sure the section match group  ahadm is there
    sshd_handler:
        section: matchgroup
        matchgroup: ahadm
        state: present
```

Place a directive in a match user section
```yaml
  - name: Make sure the section match user ar007310 is there
    sshd_handler:
        section: matchuser
        matchuser: ar007310
        state: present
```

Make sure the match group section isn't there
```yaml
  - name: Remove match group ahadm section
    sshd_handler:
        section: matchgroup
        matchgroup: ahadm
        state: absent
```

Make sure the match user section section isn't there
```yaml
  - name: Remove match user ar007310 section
    sshd_handler:
        section: matchuser
        matchuser: ar007310
        state: absent
```

----------------------------------------------------------------------------------------------------------------------------

sshd_handler_cmd command
=========================
* This is a python program to handle sshd configuration files
In order to run it i recommned to follow this steps
    1 - Copy the sshd_handler_cmd.py and the sshd_hndlers_lib.py to a defined dir. Example /opt/scripts
    2 - create a script called sshd_handler_cmd in the same directory with this content
```bash
if [ -f /usr/bin/python3 ]; then 
        python3  /opt/scripts/sshd_handler_cmd.py $@
    else
        echo "ERR: You need python3"
    fi
```
    3 - Create a symbolic link in /usr/bin/, in order to have the script in the path
```bash
ln -s /opt/scripts/sshd_handler_cmd /usr/bin/sshd_handler_cmd
``` 

Then you will be able to run as this
    sshd_handler_cmd -h
to see how to use it.

Author Information
------------------
Role and modules developed by Luciano Baez (lucianobaez@kyndryl.com or lucianobaez1@ibm.com), working for the GI-SVC-GBSE team.
https://github.kyndryl.net/lucianobaez
https://github.ibm.com/lucianobaez1


Personal contact on lucianobaez@outlook.com ( https://github.com/luciano-baez )


