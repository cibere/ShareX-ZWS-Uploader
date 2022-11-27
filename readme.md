# a zws sharex uploader in python

feel free to make pr's

## Self-Hosting

1. [Install Python](https://www.python.org)
1. open your console, cd into the directory, and run `pip install -r requirements.txt`
1. Now create a file called `secrets.txt`, and put your token there. I recommend something safe and secure.
1. Finally, run `py main.py` (or `python main.py` depending on your installation) to start up the webserver.
1. As for your ShareX Settings, just copy what I have here (ofc edit stuff like your token and domain)

![Method: Post, Headers: {token: your token}, URL: {json:url}, deletion url: {json:deletion_url}, file form name: data, body: form data (multipart/form-data), request URL: your.domain/upload](https://i.imgur.com/xfz4B0I.png)
