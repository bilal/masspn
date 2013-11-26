#!/usr/bin/env python
# author: msheikhh@ea.com
# A small command line utility for sending out mass push notifications. 
# Notifications are sent to all registered users for an application.

import getopt, sys
from boto import sns
import multiprocessing as mp
from time import sleep
#from multiprocessing.pool import ThreadPool

def usage():
	print 'Usage: masspn.py [-v] [--dry-run] [-a arns_file] [-g region] [-m message] [-s message-structure] [-n num_processes] '

def require_param(param):
	print 'Error: must specify %s' % param
	usage()
	sys.exit(2)
	

def process_chunk(chunk, message, region, message_structure, output_filename, dry_run):
	disabled = []
	arns_to_process = []
	successes = []
	failures = []
	try:
		print "Process chunk called with chunk size: %d, message: %s, output_filename: %s and dry_run: %s" % (len(chunk), message, output_filename, str(dry_run))
		for line in chunk:
			try:
				#print "line: %s" % line
				if line.strip():
					[arn, enabled] = line.strip().split(",")
					#print "arn: %s, enabled: %s" % (arn, enabled)
					if (enabled == "false"):
						disabled.append(arn)
					else:
						arns_to_process.append(arn)
			except Exception as err:
				print "Error parsing line: %s" % line
		successes, failures = send_pns(arns_to_process, message, region, message_structure, dry_run)
	except Exception as e:
		print "Error processing chunk: %s" % str(e)
	return (successes, failures, disabled, output_filename)

def send_pns(arns, message, region, message_structure, dry_run):
	print "Send pns called with message: %s, dry_run: %s, %d arns, region: %s, message_structure: %s" % (message, str(dry_run), len(arns), region, message_structure)
	successes = []
	failures = []
	try:
		c = sns.connect_to_region(region)
		for arn in arns:
			if not dry_run:
				c.publish(None, message, None, arn, "json")
			else:
				# sleep to simiulate request time
				sleep(0.2) # 200 milliseconds
			successes.append(arn)
	except Exception as err:
		print "Error sending push notification: %s" % str(err)
		failures.append(arn)
	return (successes, failures)
	
def handle_process_chunk_result(result):
	#print "Handle process chunk result called with: %s" % str(result)
	(successes, failures, disabled, filename) = result
	s = len(successes)
	f = len(failures)
	d = len(disabled)
	total = s + f + d
	append_arns_to_file(successes, filename, "success")
	append_arns_to_file(failures, filename, "failures")
	append_arns_to_file(disabled, filename, "disabled")
	print "A chunk of %d processed with %d successful notifications, %d failures and %d disabled (not sent)" % (total, s, f, d)

def append_arns_to_file(arns, filename, arn_status):
	fname = filename + "." + arn_status.lower()
	with open(fname, 'a') as f:
		for arn in arns:
			f.write("%s\n" % arn)
		f.close()
		
def initialize_file(filename):
	f = open(filename, 'w')
	f.write('')
	f.close()

def main():
	try:
		opts, args = getopt.getopt(sys.argv[1:], 'hva:g:m:s:n:',['help', 'verbose', 'dry-run', 'arns-file', 'region', 'message', 'message-structure', 'num-processes'])
	except:
		usage()
		sys.exit(2)
		
	arns_file = ''
	message = ''
	message_structure = ''
	region = ''
	num_processes = 5
	verbose = False
	dry_run = False
	# process 500 arns in a go
	chunk_size = 500 
	
	for o, a in opts:
		if o in ('-h', '--help'):
			usage()
			sys.exit()
		if o in ('-v', '--verbose'):
			verbose = True
		if o in ('-a', '--arns-file'):
			arns_file = a
		if o in ('-m', '--message'):
			message = a
		if o in ('-s', '--message-structure'):
			message_structure = a
		if o in ('-g', '--region'):
			region = a
		if o in ('-n', '--num-processes'):
			num_processes = int(a)
		if o == '--dry-run':
			dry_run = True
	
	if arns_file == '':
		require_param("arns file")
	if message == '':
		require_param("message")
	if region == '':
		require_param("region (e.g., us-east-1, us-west-2)")
	if (message_structure == '') or (message_structure != 'text' and message_structure != 'json'):
		require_param("message structure (text or json)")

	print "Dry run: %s" % dry_run
	output_file = arns_file + ".out"
	
	initialize_file(output_file + ".success")
	initialize_file(output_file + ".failures")
	initialize_file(output_file + ".disabled")
	
	arn_count = 0
	try:
		# create a process pool
		pool = mp.Pool(processes = num_processes)
		#pool = ThreadPool(processes = num_processes)
		
		with open(arns_file, 'r') as f:
			while True:
				chunk = []
				for l in xrange(0, chunk_size):
					line = f.readline()
					if not line:
						break
					chunk.append(line)		
				arn_count += len(chunk)
				# process the chunk
				pool.apply_async(process_chunk, args = (chunk, message, region, message_structure, output_file, dry_run), callback = handle_process_chunk_result)
				print "Update: Issued async processing requests for %d arns" % arn_count
				if len(chunk) < chunk_size:
					break
			f.close()
		pool.close()
		pool.join()
		print "Successfully processed all (%d) arns in %s" % (arn_count, arns_file)
	except Exception as err:
		print "Error: Stopped processing with error %s" % str(err)
		print "Issued processing requests for %d arns from %s" % (arn_count, arns_file)
		print "Please check the output files %s*" % output_file
		sys.exit(2)
				
if __name__ == "__main__":
	main()
