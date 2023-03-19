from flask import Flask,render_template,redirect,request,url_for
from flask_autoindex import AutoIndex
import urllib.parse
import urllib.request
import requests
import os
from os.path import exists
from configparser import ConfigParser
import string
import random

global postCount
postCount = 0
global pstCntCheck
pstCntCheck = 0
global fredslistPosts
fredslistPosts  = '/root/DogBox/static/fredslist/posts'
global fredslistPostsList
fredslistPostsList = []

def make_tree(path):
	tree = dict(name=os.path.basename(path), children=[])
	try: lst = os.listdir(path)
	except OSError:
		pass #ignore errors
	else:
		for name in lst:
			fn = os.path.join(path, name)
			if os.path.isdir(fn):
				tree['children'].append(make_tree(fn))
			else:
				tree['children'].append(dict(name=name))
	return tree

def save_config(title, name, value):
	if not config.has_section(title):
		config.add_section(title)
		config.set(title, name, value)
		with open(fredslistPosts, 'w') as configfile:
			config.write(configfile)
			configfile.close()
		print(title+name+" has been saved to config. A new title section was created for it as it as not present beforehand. It\'s value is: "+value)
	if not config.has_option(title, name):
		config.set(title, name, value)
		with open(fredslistPosts, 'w') as configfile:
			config.write(configfile)
			configfile.close()
		print(title+name+" has been saved to config. A new option was made for it as it was not present beforehand. It\'s value is: "+value)
	if config.has_option(title, name):
		if value != config.get(title, name):
			config.set(title, name, value)
			with open(fredslistPosts, 'w') as configfile:
				config.write(configfile)
				configfile.close()
			print(title+name+" already existed, but the value being saved was different so it was overwritten. It's new value is: "+value)
		else:
			print(title+name+" already exists, and the value is the same. We won't overwite it.")

def rem_config(title, name):
	if not config.has_option(title, name):
        	print("config hasn't got: "+title+", "+name)
	else:
		print(title+", "+name+" is being removed from the config. It's value is: "+config.get(title, name))
		config.remove_option(title, name)
		with open(fredslistPosts, 'w') as configfile:
			config.write(configfile)
			configfile.close()
		print(title+", "+name+" has been removed from the config.")

app = Flask(__name__)

spath = "/home/ftpdog/"
files_index = AutoIndex(app, browse_root=spath, add_url_rules=False)
app.config['SECRET_KEY'] = "dog420lol"

config = ConfigParser() #defining configparser to config so we can shorthand it for the rest of the script

def read_config(): #read config and reassign values to variables
	global postCount
	global fredslistPostsList
	global pstCntCheck
	fredslistPostsList = []
	postCount = 0
	pstCntCheck = 0

	config.read(fredslistPosts)

	if config.has_option('POSTS', 'postCount'):
		pstCnt = config.get('POSTS', 'postCount')
		if pstCnt.isnumeric():
			postCount = int(pstCnt)
			print("postCount is: "+str(postCount))

	pstCntCheck = 0
	postSplitJoin = ""
	postSplit = ""
	postSplitTuple = ""
	for i in range(1, postCount+50):
		postSplitJoin = ""
		postSplit = ""
		postSplitTuple = ""

		if config.has_option('POSTS', 'POST-'+str(i)):
			pstCntCheck += 1
			postSplit = config.get('POSTS', 'POST-'+str(i)).split('<->')
			postSplitTuple = tuple(postSplit)
			if(postSplitTuple != ""):
				fredslistPostsList.append(postSplitTuple)

		if not config.has_option('POSTS', 'POST-'+str(i)):
			postSplitJoin = ""
			postSplit = ""
			postSplitTuple = ""
			ni = i
			while not config.has_option('POSTS', 'POST-'+str(i)):
				ni += 1
				if config.has_option('POSTS', 'POST-'+str(ni)):
					postSplit = config.get('POSTS', 'POST-'+str(ni)).split('<->')
					postSplit[2] = str(i)
					postSplitTuple = tuple(postSplit)
					postSplitJoin = "<->"
					postSplitJoin = postSplitJoin.join(postSplitTuple).replace("%", "%%")
					rem_config('POSTS', 'POST-'+str(ni))
					save_config('POSTS', 'POST-'+str(i), postSplitJoin)
					#print(postSplitTuple)
					if(postSplitTuple != ""):
						fredslistPostsList.append(postSplitTuple)

					if config.has_option('POSTS', 'POST-'+str(i)):
						pstCntCheck += 1
						postSplit = config.get('POSTS', 'POST-'+str(i)).split('<->')
						postSplitTuple = tuple(postSplit)
						if(postSplitTuple != ""):
							fredslistPostsList.append(postSplitTuple)
						break
				if (ni > postCount+50):
					break
			save_config('POSTS', 'postCount', str(pstCntCheck))
			postCount = pstCntCheck
			print("postCount is equal to pstCntCheck. It's now: "+str(postCount))
			print(fredslistPostsList, type(fredslistPostsList))

read_config() # read config before script starts and reload/re-assign variables

def submitInformation(url,parameters):
	encodedParams = urllib.parse.urlencode(parameters).encode("utf-8")
	req = urllib.request.Request(url)
	net = urllib.request.urlopen(req,encodedParams)
	return(net.read())

url = "http://simhost-04759f8c54b30a5ca.agni.secondlife.io:12046/cap/11f74117-1ceb-eedf-656e-603ea8abcb61" # set manually from the URL provided in chat after running the LSL script
parameters = {'color':'white'}



@app.route("/")  # this sets the route to this page
def home():
	return render_template('index.html')

@app.route("/minecraft/")
def minecraft():
	return render_template('minecraft.html')

@app.route("/", subdomain="radio")
@app.route("/radio/")
def radio():
	# ident.me prints ur ip address in clear text when u visit it, very handy for scripts like this
	external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
	stream_ip = "http://{extIP}:1337/stream".format(extIP=external_ip)
	return redirect(stream_ip, code=302)

@app.route("/fredslist/")
def fredslist():
	print("\n\nMain Page Loaded.\n\n")
	read_config()
	return render_template('fredslist.html', fredslistPostsList=fredslistPostsList)
@app.route("/fredslist/makelisting", methods=['GET', 'POST'])
def fredslistmakelisting():
	print("\n\nMake Listing Page Loaded.\n\n")
	global postCount
	read_config()

	if request.method == 'POST':
		if not exists(fredslistPosts):
			f = open(fredslistPosts, "x")
			f.close()

		postCount += 1
		save_config("POSTS", "postCount", str(postCount))
		imageURL = request.form['imageURL'].replace('%', '%%')
		message = request.form['message']
		secretKey = request.form['secretKey']
		save_config("POSTS", "POST-"+str(postCount), imageURL+"<->"+message+"<->"+str(postCount)+"<->"+secretKey)
		read_config()
		return redirect(url_for('fredslist'))

	else:
		read_config()
		randomSecretKey = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(6))
		return render_template('fredslistmakelisting.html', randomSecretKey=randomSecretKey)

@app.route("/fredslist/editlisting", methods=['GET', 'POST'])
def fredslisteditlisting():
	print("\n\nEdit Listing Page Loaded.\n\n")
	global postCount

	if request.method == 'POST':
		if not exists(fredslistPosts):
			f = open(fredslistPosts, "x")
			f.close()

		# i can't fucking get this motherfucking delete shit to work
		#if request.form.get("deletebutton") == "DELETE":
			#if request.form['delete'] == "DELETE":
				#formPostID = request.form['postID']
				#formSecretKey = request.form['secretKey']
				#post = fredslistPostsList[int(formPostID)-1] # -1 cuz list starts at 0 and we start at 1
				#if(formSecretKey == post[3]):
					#print("removing ID "+str(formPostID)+". Sending remove config command now with: POST-"+str(formPostID))
					#rem_config('POSTS', 'POST-'+str(formPostID))
					#read_config()
					#return redirect(url_for('fredslist'))
				#else:
					#return "Secret Key was incorrect. Please try again.", 400
			#else:
				#return "You didn't type 'DELETE' into the delete box.", 400

		elif request.form.get("submitbutton") == "Submit Changes":
			formPostID = request.form['postID']
			formSecretKey = request.form['secretKey']
			print('formPostID: '+formPostID)
			post = fredslistPostsList[int(formPostID)-1] # have to -1 cuz list starts at 0 and our posts start at 1
			if(formSecretKey == post[3]):
				imageURL = request.form['imageURL'].replace('%', '%%')
				message = request.form['message']
				save_config("POSTS", "POST-"+str(formPostID), imageURL+"<->"+message+"<->"+str(formPostID)+"<->"+formSecretKey)
				read_config()
				return redirect(url_for('fredslist'))
			else:
				return "Secret Key was incorrect. Please try again.", 400
	else:
		read_config()
		return render_template('fredslisteditlisting.html', fredslistPostsList=fredslistPostsList)

@app.route("/ftp/")
@app.route("/ftp/files/<path:path>")
def autoindex(path="."):
	return files_index.render_autoindex(path)

@app.route("/RemotePrimManipulation/")
def RemotePrimManipulation():
	return render_template('primManip.html')

@app.route("/RemotePrimManipulation/red/")
def red():
	print('Prim remotely changed colors to Red.')
	parameters = {'color':'red'}
	info = submitInformation(url,parameters)
	return render_template('primManip.html')

@app.route("/RemotePrimManipulation/green/")
def green():
	print('Prim remotely changed colors to Green.')
	parameters = {'color':'green'}
	info = submitInformation(url,parameters)
	return render_template('primManip.html')

@app.route("/RemotePrimManipulation/blue/")
def blue():
	print('Prim remotely changed colors to Blue.')
	parameters = {'color':'blue'}
	info = submitInformation(url,parameters)
	return render_template('primManip.html')

if __name__ == '__main__':
	app.run()
