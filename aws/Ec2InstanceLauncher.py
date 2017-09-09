import boto.ec2
import argparse
from pprint import pprint
from time import sleep

DEFAULT_REGION = "eu-west-1" # Ireland
DEFAULT_AMI_IMAGE_ID = "ami-5f2f5528" # CoreOS-stable-681.2.0-hvm
DEFAULT_INSTANCE_TYPE= "t2.micro"
DEFAULT_DISK_SIZE_GB= 30
DEFAULT_VOLUME_DIRECTORY = "/dev/xvda" # CoreOS device mount location

KEY_NAME = None
SECURITY_GROUPS_NAMES = None
REGION = None
AMI_IMAGE_ID = None
INSTANCE_TYPE = None
DISK_SIZE_GB = None
VOLUME_DIRECTORY = None
NAME = None
ROLE_PROFILE = None

def parse_commandline_arguments():

	global KEY_NAME
	global SECURITY_GROUPS_NAMES
	global REGION
	global AMI_IMAGE_ID
	global INSTANCE_TYPE
	global DISK_SIZE_GB
	global VOLUME_DIRECTORY
	global NAME
	global ROLE_PROFILE
	
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,description='Create an AWS instance with the specified key name and security groups.')
	parser.add_argument("keyname", type=str, help="The key name to use as created in AWS console")
	parser.add_argument("security_group_name",type=str, help="The security group name to use as created in AWS console")
	parser.add_argument("-r","--region", dest="region", type=str, default=DEFAULT_REGION, help="Specify the global region to create instance in")
	parser.add_argument("-i","--image-id", dest="image_id", type=str, default=DEFAULT_AMI_IMAGE_ID, help="Specify the image ID to create instance from")
	parser.add_argument("-t","--instance-type", dest="instance_type", type=str, default=DEFAULT_INSTANCE_TYPE, help="Specify the instance type to create instance from")
	parser.add_argument("-d","--disk-size", dest="disk_size", type=int, default=DEFAULT_DISK_SIZE_GB, help="Specify the disk size in GB")
	parser.add_argument("-v","--volume-directory", dest="volume_directory", type=str, default=DEFAULT_VOLUME_DIRECTORY, help="Specify the directory to create volume mount in")
	parser.add_argument("-n","--name", dest="name_tag", type=str, help="Specify the name of the instance and volume to be created")
	parser.add_argument("-p","--role-profile", dest="profile", type=str, help="Specify the IAM role profile to apply to this instance")
	
	args = parser.parse_args()

	print ("Attempting to create an AWS Instance using the following parameters:")
	pprint(vars(args))

	KEY_NAME = args.keyname
	SECURITY_GROUPS_NAMES = args.security_group_name
	REGION = args.region
	AMI_IMAGE_ID = args.image_id
	INSTANCE_TYPE = args.instance_type
	DISK_SIZE_GB = args.disk_size
	VOLUME_DIRECTORY = args.volume_directory

	if args.name_tag:
		NAME = args.name_tag

	if args.profile:
		ROLE_PROFILE = args.profile


def launch_instance():

	connection = create_connection_to_region()
	reservation = create_instance(connection)
	instance = get_instance_from_reservation(reservation)
	address = create_elastic_ip_address(connection)
	assign_elastic_ip_address(connection, instance.id, address)

	if NAME is not None:
		assign_name_tag_to_instance(connection, instance.id)
		assign_name_tag_to_volume(connection, instance.id)

	instance_details = get_instance_details(connection, instance.id)

	print ("====================")
	print ("Instance details:")
	pprint(instance_details.__dict__)
	
	
def create_connection_to_region():

	print ("====================")
	print ("Attempting to connect to region: %s" % REGION)
	
	connection = boto.ec2.connect_to_region(REGION)

	if connection is None:
		raise ConnectionError("Could not connect to region! Check your connection or region") 
	
	print ("Connection to region %s made succesfully!" % REGION)
	return connection


def create_instance(connection):

	user_data = get_user_data()
	block_device_map = create_block_device_mapping()
	print ("====================")
	print ("Attempting to create and run instance using the following details -")
	print ("Image ID : %s, Key name: %s, Security group: %s, Instance type: %s, User data: %s" %(AMI_IMAGE_ID, KEY_NAME, SECURITY_GROUPS_NAMES, INSTANCE_TYPE, user_data))
	
	reservation = connection.run_instances (AMI_IMAGE_ID,
		key_name = KEY_NAME,
		security_groups=[SECURITY_GROUPS_NAMES],
		user_data=user_data,
		instance_type=INSTANCE_TYPE,
		block_device_map = block_device_map,
		instance_profile_name=ROLE_PROFILE)

	if reservation is None:
		raise Exception( "Reservation not created! Try again")

	print ("Reservation created succesfully! Details - Reservation ID: %s, Owner ID: %s, Security Groups: %s, Instances: %s" % (reservation.id, reservation.owner_id, reservation.groups, reservation.instances))
	
	if len(reservation.instances) == 0:
		raise Exception ("There is no created instance from this attempt!")
	
	return reservation


def get_user_data():

	cloud_config ="""#cloud-config
coreos:
  etcd:
    discovery: https://discovery.etcd.io/<write_your_own_id>
    addr: $private_ipv4:4001
    peer-addr: $private_ipv4:7001
  units:
    - name: etcd.service
      command: start
    - name: fleet.service
      command: start"""

	return cloud_config


def create_block_device_mapping():

	print ("====================")
	print ("Creating block device volume size %s GB of type %s in volume directory %s" % (DISK_SIZE_GB, "gp2", VOLUME_DIRECTORY))

	block_device_type = boto.ec2.blockdevicemapping.BlockDeviceType(size=DISK_SIZE_GB,volume_type="gp2")

	block_device_mapping = boto.ec2.blockdevicemapping.BlockDeviceMapping()
	block_device_mapping [VOLUME_DIRECTORY] = block_device_type

	print ("Block device created successfully!")

	return block_device_mapping

def get_instance_from_reservation(reservation):

	print ("====================")
	print ("Getting created instance from reservation...")
	
	instance = reservation.instances[0]

	if instance is None:
		raise Exception ("Instance does not exist! Check the AWS console to verify creation or try again")

	print ("Instance created and launched successfully!")

	return instance

def create_elastic_ip_address(connection):

	print ("====================")
	print ("Creating an Elastic IP...")

	address = connection.allocate_address()

	if address is None:
		print("Elastic IP address creation failed! Check the AWS console to verify and perform action manually.")
		
	else:
		print("Elastic IP address details:")
		pprint(address.__dict__)
		print("Elastic IP address created successfully!")

	return address

	
def assign_elastic_ip_address(connection,instance_id, address):

	print ("====================")
	
	if address is None:
		print("Elastic IP does not exist. Skipping assingment step...")

	else:
		print ("Assigning an Elastic IP to instance %s" % instance_id)
		
		wait_for_instance_to_be_running(connection, instance_id)
		successful_association= connection.associate_address(instance_id=instance_id, allocation_id=address.allocation_id)

		if successful_association:
			print("Elastic IP address assignment successful!")

		else:
			print("Elastic IP address assignment failed! Check the AWS console to verify and perform action manually.")

def wait_for_instance_to_be_running(connection,instance_id):

	instance_state_code = None
	while instance_state_code is not 16:
		print ("Waiting for instance state to be 'running'")
		sleep(5)
		instance = get_instance_details(connection,instance_id)
		instance_state_code = instance.state_code

def assign_name_tag_to_instance(connection, instance_id):

	print ("====================")
	print("Assigning name tag %s to instance %s" %(NAME,instance_id))

	connection.create_tags([instance_id],{"Name": NAME})
	print ("Name tag applied to instance successfully!")

def assign_name_tag_to_volume(connection, instance_id):

	print ("====================")
	volume_name_tag = NAME + "_volume"
	volumes = connection.get_all_volumes(filters={'attachment.instance-id': instance_id})

	if len(volumes) == 0:
		print("There are no volumes associate with this instance! Name tag cannot be assigned. Check the AWS console to verify and perform action manually")

	else:
		for volume in volumes:
			print("Assigning name tag %s to volume %s" % (volume_name_tag,volume.id))
			connection.create_tags([volume.id],{"Name": volume_name_tag})
			print ("Name tag applied to volume successfully!")

def get_instance_details(connection, instance_id):

	instances = connection.get_only_instances(instance_ids=[instance_id])
	instance = instances[0]
	return instance


if __name__ == "__main__":

	try:
		parse_commandline_arguments()
		launch_instance()
	except Exception as error:
		print (str(error))
