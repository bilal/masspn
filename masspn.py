#!/usr/bin/env python
# author: msheikhh@ea.com
# A small command line utility for sending out mass push notifications inspired by cq. Notifications are sent to all registered users for an application.

import getopt, sys
from boto.sns.connection import SNSConnection

def usage():
	print 'Usage: masspn.py [-v] [-a sns_app_arn] [-m message] [-n num_threads] '

def require_param(param):
	print 'Error: must specify %s' % param
	usage()
	sys.exit(2)

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hva:m:n:',['help', 'verbose', 'app-arn', 'message', 'num-threads'])
	except:
		usage()
		sys.exit(2)
		
	app_arn = ''
	message = ''
	num_threads = 1
	verbose = False
	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit()
		if o in ('-v', '--verbose'):
			verbose = True
		if o in ('-a', '--sns_app_arn'):
			app_arn = a
		if o in ('-m', '--message'):
			message = a
		if o in ('-n', '--num_threads'):
			num_threads = int(a)
	
	if app_arn == '':
		require_param("sns application arn")
	if message == '':
		require_param("message")
	
	c = SNSConnection()
	
	total_arns = 0
	successes = 0
	not_sent = 0
	failures = 0
	next_token = None
	
	#print c.list_platform_applications()
	
	while True:
		endpoint_result = c.list_endpoints_by_platform_application(app_arn)
		next_token = endpoint_result['ListEndpointsByPlatformApplicationResponse']['ListEndpointsByPlatformApplicationResult']['NextToken']
		endpoints = endpoint_result['ListEndpointsByPlatformApplicationResponse']['ListEndpointsByPlatformApplicationResult']['Endpoints']
		total_arns += len(endpoints)
		print "Got %d more arns. Total arns %d" % (len(endpoints), total_arns)
		print "Next token: %s" % next_token
		# send notifications
		for endpoint in endpoints:
			try:
				endpoint_arn = endpoint['EndpointArn']
				endpoint_enabled = endpoint['Attributes']['Enabled']
				if (endpoint_enabled == 'false'):
					print "Endpoint not enabled: Not Sending push notification to %s" % endpoint_arn
					not_sent += 1 
				else:
					print "Sending push notification to %s" % endpoint_arn
					c.publish(None, message, None, endpoint_arn, None)
					successes += 1
			except Exception, err:
				print "Error sending push notification: %s" % str(err)
				failures += 1
				
				
		if next_token == None:
			break
			
	# print statistics
	print "Statistics:"
	print "Successes: %s, Failures: %s, Not Sent (Disabled): %s, Total: %s" % (successes, failures, not_sent, total_arns)
	
if __name__ == "__main__":
	main()
