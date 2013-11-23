A command-line utility to send mass push notifications to all users of SNS application. 

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