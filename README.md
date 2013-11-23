A command-line utility to send mass push notifications to all registered users of an SNS application. 

### Setup:

* Install easy_install (https://pypi.python.org/pypi/setuptools)
* Install pip: sudo easy_install pip
* Install Boto (AWS SDK for python): sudo pip install boto

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

### Running the script:

<blockqoute>
	
	Usage: masspn.py [-v] [-a sns_app_arn] [-m message] [-n num_threads]
	
</blockquote>