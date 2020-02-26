#!/usr/bin/expect -f
set timeout 20
set username "admin"

#set password "VF-EShg556"
set password "VFIE-hg556"

set ip "192.168.1.1"
# Read command as arg to this script
set cmd [lindex $argv 0]
spawn telnet $ip
expect "Login:"
send -- "$username\r"
expect "Password:"
send -- "$password\r"
expect " > "
send -- "$cmd\r"
expect " > "
send -- "^D"
