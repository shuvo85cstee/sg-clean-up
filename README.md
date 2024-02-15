# sg-clean-up
This script was developed when I found a VPC having 157 Security groups and all of them have a rule of allowing RDP from everywhere. 
I had to remove that rule and add a rule which will only allow RDP from bastion/vpn ip.

Script improvement plan:
1. modularize codes
2. Add checks for ipv6 rules exists
3. Add loggging ( every rules added/deleted will be logged in s3)
