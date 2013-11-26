#!/usr/bin/env python
# author: msheikhh@ea.com
# Fetch all registered users (endpoints) of an SNS platform application.
# Writes the arns in a file in append mode.  

import getopt, sys
from boto import sns

def usage():
	print 'Usage: fetch_user_arns.py [-v] [-a sns_app_arn] [-g region] [-o output_file]'

def require_param(param):
	print 'Error: must specify %s' % param
	usage()
	sys.exit(2)

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hva:g:o:',['help', 'verbose', 'app-arn', 'region', 'output-file'])
	except:
		usage()
		sys.exit(2)
		
	app_arn = ''
	output_file = ''
	region = ''
	verbose = False
	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit()
		if o in ('-v', '--verbose'):
			verbose = True
		if o in ('-a', '--sns_app_arn'):
			app_arn = a
		if o in ('-g', '--region'):
			region = a
		if o in ('-o', '--output'):
			output_file = a
	
	if app_arn == '':
		require_param("sns application arn")
	if output_file == '':
		require_param("output_file")
	if region == '':
		require_param("region (e.g., us-east-1, us-west-2)")
	
	#c = SNSConnection()
	c = sns.connect_to_region(region)
	
	total_arns = 0
	next_token = None
	retries = 5
	failures = 0
	
	with open(output_file, 'w') as f:
		while failures < retries:
			try:
				endpoint_result = c.list_endpoints_by_platform_application(app_arn, next_token)
				next_token = endpoint_result['ListEndpointsByPlatformApplicationResponse']['ListEndpointsByPlatformApplicationResult']['NextToken']
				endpoints = endpoint_result['ListEndpointsByPlatformApplicationResponse']['ListEndpointsByPlatformApplicationResult']['Endpoints']
				total_arns += len(endpoints)
				print "Got %d more arns. Total arns %d" % (len(endpoints), total_arns)
				print "Next token: %s" % next_token
				# write to file
				for endpoint in endpoints:
					endpoint_arn = endpoint['EndpointArn']
					endpoint_enabled = endpoint['Attributes']['Enabled']
					f.write("%s,%s\n" % (endpoint_arn, endpoint_enabled))
				print "Arns written to %s" % output_file
				# reset failures
				failures = 0 
				# check if there are any more arns
				if next_token == None:
					break
			except Exception, err:
				print "Error fetching user arns: %s" % str(err)
				failures += 1
		f.close()
				
	if (failures >= retries):
		sys.exit("Error fetching arns for platform application %s" % app_arn)
	else:
		print "Successfully fetched %d user arns for platform application %s" % (total_arns, app_arn)
		sys.exit(0)
		
if __name__ == "__main__":
	main()
