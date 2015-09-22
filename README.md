# aws-ec2-instance-creator
A Python 3 command line script with arguments to create AWS EC2 Instances in your account

# Introduction

This article is a guide on using the EC2 Instance Launcher Python script to create AWS instances. 

# Pre-requisites

There is some setup work to be done before being able to use the script. You may refer to the [getting started][] guide, but specifics are covered below:

1) You must install Python 3

2) You must install the ```boto``` Python package. You can do this by executing the following command:

```
pip3 install boto
```

3) You must configure boto, by creating a configuration file. The configuration must contain the following:

```
[Credentials]
aws_access_key_id = YOURACCESSKEY
aws_secret_access_key = YOURSECRETKEY
```

Your ```access_key_id``` and ```aws_secret_access_key``` are provided to you when you first create your account. You cannot retrieve the values again, but can regenerate them in the AWS console.

On Mac/Unix computers, the boto config file must be created in the the file ```~/.boto```

On Windows computers, create any file but set a user environment variable named ```BOTO_CONFIG``` to the full path of that file.

You can read up further about [boto config][]

# Using the script

When you clone the repository you will see a file entitled ```Ec2InstanceLauncher.py``` in the ```aws``` folder.

You can see how to use this script by running the script with the ```-h``` or ```--help``` flag to understand its usage

```
$ python3 Ec2InstanceLauncher.py -h
usage: Ec2InstanceLauncher.py [-h] [-r REGION] [-i IMAGE_ID]
                              [-t INSTANCE_TYPE] [-d DISK_SIZE]
                              [-v VOLUME_DIRECTORY]
                              keyname security_group_name

Create an AWS instance with the specified key name and security groups.

positional arguments:
  keyname               The key name to use as created in AWS console
  security_group_name   The security group name to use as created in AWS
                        console

optional arguments:
  -h, --help            show this help message and exit
  -r REGION, --region REGION
                        Specify the global region to create instance in
                        (default: eu-west-1)
  -i IMAGE_ID, --image-id IMAGE_ID
                        Specify the image ID to create instance from (default:
                        ami-5f2f5528)
  -t INSTANCE_TYPE, --instance-type INSTANCE_TYPE
                        Specify the instance type to create instance from
                        (default: t2.micro)
  -d DISK_SIZE, --disk-size DISK_SIZE
                        Specify the disk size in GB (default: 30)
  -v VOLUME_DIRECTORY, --volume-directory VOLUME_DIRECTORY
                        Specify the directory to create volume mount in
                        (default: /dev/xvda)

```

There are 2 mandatory arguments you must provide: ```keyname``` and ```security_group_name```. the ```keyname``` is the AWS key you would like to use to create the ssh key access of the primary account for the instances to be created. the ```security_group_name``` is the AWS security group that you would like to use to apply security settings on the instance to be created.

There are several optional arguments you can provide aswell. These optional arguments have default values set that will be used unless you specify other values for them. Currently the opitonal values are set to create a CoreOS 681.2.0 server with 30 GB of disk space in volume mount folder /dev/xda. The instance type is the t2.micro, creating this instance in Ireland (eu-west-1).   
(Note: If you do want to proceed with CoreOS instance creation, your security group must have ports 4001 and 7001 open)

You can now run the script to create an instance, which will output information on the console as it executes:

```

$ python3 Ec2InstanceLauncher.py hakanozbay-key-pair-ireland hakanozbay_SG_euireland
Attempting to create an AWS Instance using the following parameters:
{'disk_size': 30,
 'image_id': 'ami-5f2f5528',
 'instance_type': 't2.micro',
 'keyname': 'hakanozbay-key-pair-ireland',
 'region': 'eu-west-1',
 'security_group_name': 'hakanozbay_SG_euireland',
 'volume_directory': '/dev/xvda'}
====================
Attempting to conenct to region: eu-west-1
Connection to region eu-west-1 made succesfully!
====================
Creating block device volume size 30 GB of type gp2 in volume directory /dev/xvda
Block device created successfully!
====================
Attempting to create and run instance using the following details -
Image ID : ami-5f2f5528, Key name: hakanozbay-key-pair-ireland, Security group: hakanozbay_SG_euireland, Instance type: t2.micro, User data: #cloud-config

coreos:
  etcd:
    discovery: https://discovery.etcd.io/abcdef
    addr: $private_ipv4:4001
    peer-addr: $private_ipv4:7001
  units:
    - name: etcd.service
      command: start
    - name: fleet.service
      command: start
Reservation created succesfully! Details - Reservation ID: r-1ec482b4, Owner ID: 824654475944, Security Groups: [], Instances: [Instance:i-570e9df6]
====================
Getting created instance from reservation...
Instance details:
{'_in_monitoring_element': False,
 '_placement': eu-west-1b,
 '_previous_state': None,
 '_state': pending(0),
 'ami_launch_index': '0',
 'architecture': 'x86_64',
 'block_device_mapping': {},
 'client_token': '',
 'connection': EC2Connection:ec2.eu-west-1.amazonaws.com,
 'dns_name': '',
 'ebs_optimized': False,
 'eventsSet': None,
 'group_name': None,
 'groups': [<boto.ec2.group.Group object at 0x1032d8160>],
 'hypervisor': 'xen',
 'id': 'i-570e9df6',
 'image_id': 'ami-5f2f5528',
 'instance_profile': None,
 'instance_type': 't2.micro',
 'interfaces': [NetworkInterface:eni-96d858df],
 'ip_address': None,
 'item': '\n        ',
 'kernel': None,
 'key_name': 'hakanozbay-key-pair-ireland',
 'launch_time': '2015-08-19T20:16:18.000Z',
 'monitored': False,
 'monitoring': '\n            ',
 'monitoring_state': 'disabled',
 'persistent': False,
 'platform': None,
 'private_dns_name': 'ip-172-31-42-223.eu-west-1.compute.internal',
 'private_ip_address': '172.31.42.223',
 'product_codes': [],
 'public_dns_name': '',
 'ramdisk': None,
 'reason': '',
 'region': RegionInfo:eu-west-1,
 'requester_id': None,
 'root_device_name': '/dev/xvda',
 'root_device_type': 'ebs',
 'sourceDestCheck': 'true',
 'spot_instance_request_id': None,
 'state_reason': {'code': 'pending', 'message': 'pending'},
 'subnet_id': 'subnet-2a62d15d',
 'tags': {},
 'virtualization_type': 'hvm',
 'vpc_id': 'vpc-53f62b36'}
====================
Instance created and launched successfully!

``` 

After this is done, you can check on the AWS console to verify that the volume and instance has been created.
(Note: for CoreOS servers, the service discovery URL is applicable for 10 servers in the cluster)

[boto config]: http://boto.readthedocs.org/en/latest/boto_config_tut.html
[getting started]: http://boto.readthedocs.org/en/latest/getting_started.html


