#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import boto3
client = boto3.client('ec2', region_name='us-east-1')

# Specify your VPN IP address
vpn_ip = '1.2.3.x/32'

# List out total number of Security group exists in VPC
print ('Total number of Security groups including default security group are:'
       , len(client.describe_security_groups(Filters=[{'Name': 'vpc-id'
       , 'Values': ['vpc-xxxxx']}])['SecurityGroups']))

# Generate list of Security groups IDs
sg_group_id_list = []
for f_group in \
    client.describe_security_groups(Filters=[{'Name': 'vpc-id',
                                    'Values': ['vpc-xxxxx'
                                    ]}])['SecurityGroups']:
    sg_group_id_list.append(f_group['GroupId'])

# Looping through all Security groups to remove open rdp rules and add bastion rules
for i in range(0, len(sg_group_id_list)):
    response = \
        client.describe_security_groups(GroupIds=[sg_group_id_list[i]])
    current_rules = response['SecurityGroups'][0]['IpPermissions']

    # Warm up lists to hold rules
    rdp_rules_to_remove = []
    rdp_rules_to_add = []

    # Checking in bastion/vpn rules exists. If exists, verify and no action. If does not exists, add rule.
    for rule in current_rules:
        if rule['IpProtocol'] == 'tcp' and rule['FromPort'] == 3389 \
            and vpn_ip == rule['IpRanges'][0]['CidrIp']:
            rdp_rules_to_add.append(rule)
    
    for rule in current_rules:
        if rule['IpProtocol'] == 'tcp' and rule['FromPort'] == 3389 \
            and '0.0.0.0/0' == rule['IpRanges'][0]['CidrIp']:
            rdp_rules_to_remove.append(rule)
    
    print("remove rules", rdp_rules_to_remove)
   
    # Remove wide open RDP rules
    for rule in rdp_rules_to_remove:
        client.revoke_security_group_ingress(GroupId=sg_group_id_list[i],
                IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': 3389,
            'ToPort': 3389,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
            }])

    # Add a new rule to allow RDP only from VPN IP
    if not rdp_rules_to_add:
        client.authorize_security_group_ingress(GroupId=sg_group_id_list[i],
                IpPermissions=[{
            'IpProtocol': 'tcp',
            'FromPort': 3389,
            'ToPort': 3389,
            'IpRanges': [{'CidrIp': vpn_ip}],
            }])
