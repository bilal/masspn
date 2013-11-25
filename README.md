A command-line utility for send mass push notifications to all registered users of an SNS platform application. 

### Setup:

* **Install easy_install:** https://pypi.python.org/pypi/setuptools
* **Install pip:** sudo easy_install pip
* **Install Boto (AWS SDK for python):** sudo pip install boto

### Boto Config:

Set your credentials in `~/.boto`. Create the file if it dose not exist

<blockqoute>
	
	[Credentials]
	aws_access_key_id = <your access key>
	aws_secret_access_key = <your secret key>
		
	[Boto]
	debug = 0
	num_retries = 5
</blockquote>

### Step 1: Fetch all user arns and write them to file:

</blockquote>

	Usage: fetch_user_arns.py [-v] [-a sns_app_arn] [-o output_file]

<blockqoute>
	
The output format:

</blockquote>

	arn,enabled

<blockqoute>
	
Note that fetching all registered arns cannot be parallelized and so would take quite a bit of time for large number of users. 
	
### Step 2: Send push notifications to all users

<blockqoute>
	
	Usage: masspn.py [-v] [--dry-run] [-a arns_file] [-m message] [-n num_processes]
	
</blockquote>

By default, masspn.py uses 5 processes. Specify the `--dry-run` option to process the entire file and make sure everything works but not send the actual notification. The script writes the output to `arns_file.out.[success|failures|disabled]` files, indicating the result for each arn. 