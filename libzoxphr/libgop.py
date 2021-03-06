#!/usr/bin/env python
import socket
#libgop gopher library.
import io
import tempfile
import sys

#error types
ERR_SECURITY=2
ERR_PARSER=1
ERR_IMAGELOAD=3
ERR_NONE=0
stopget=0

#whether to filter unicode characters not in u0000 to uFFFF in python 3
py3_unicodefilter=True

print("libgop gopher library v0.2")
print("check python version...")
vers=sys.version_info[0]
if vers==2:
	print("Python 2")
else:
	print("python 3")
	import re
class mitem:
	def __init__(self, data, txtflg=0):
		self.errortype=ERR_NONE
		self.errorlabel=""
		self.errorinfo=""
		self.rect=None
		self.rect2=None
		if not isinstance(data, str) and vers==3:
			data=data.decode()
			if py3_unicodefilter:
				data=re.sub("[^\u0000-\uFFFF]", "?", data)
			#print("py3 data convert")
		if txtflg:
			self.datalist=None
			self.hostname=None
			self.selector=None
			self.gtype=None
			#self.debug=data.replace("\r\n", "[CR][LF]").replace("\r", "[CR]").replace("\n", "[LF]").replace("\t", "[TAB]")
			self.debug=""
			data=data.replace("\r\n", "").replace("\r", "").replace("\n", "").replace("\t", "        ")
			self.name=data
		else:
				
			try:
				datax=data.replace("\r\n", "").replace("\n", "")
				#handle gopher EOF dots here, so error message code is less ugly.
				if datax==".":
					self.gtype="END"
					self.name="."
					self.selector=None
					self.hostname=None
					self.port=None
					self.debug=data.replace("\r\n", "[CR][LF]").replace("\r", "[CR]").replace("\n", "[LF]").replace("\t", "[TAB]")
					self.datalist=datax
				else:
					self.gtype=datax[0]
					self.datalist=datax[1:].split("\t")
					self.name=self.datalist[0]
					self.selector=self.datalist[1]
					self.hostname=self.datalist[2]
					self.port=self.datalist[3]
					self.debug=data.replace("\r\n", "[CR][LF]").replace("\r", "[CR]").replace("\n", "[LF]").replace("\t", "[TAB]")
			#Handle index errors
			except IndexError:
				self.datalist=None
				self.hostname=None
				self.selector=None
				self.gtype=None
				self.debug=data.replace("\r\n", "[CR][LF]").replace("\r", "[CR]").replace("\n", "[LF]").replace("\t", "[TAB]")
				self.errortype=ERR_PARSER
				#treat blank lines specifically, as they are fairly common.
				if self.debug=="[CR][LF]":
					self.errorinfo="Stray Newline."
				else:
					self.errorinfo="Could not index needed feilds."
				self.errorlabel="LINE ERROR"
				self.name=data.replace("\r\n", "").replace("\r", "").replace("\n", "").replace("\t", "        ")

socketlist=[]

def menudecode(data, txtflg=0):
	menulist=[]
	for item in data:
		menulist.extend([mitem(item, txtflg)])
	return menulist
#gopherget uses tempfile as a buffer.
#if stopget is set to 1 while gopherget is reciving data, it will abruptly stop. subsequent calls will reset stopget.
#if stopget is set to 2, both active and subsequent calls will imediately stop. the latter is used upon Zoxenpher shutting down.
def gopherget(host, port, selector, query=None):
	global stopget
	global socketlist
	if stopget==1:
		stopget=0
	print("GopherGet: \"" + host + ":" + str(port) + " " + selector + "\"")
	gsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	socketlist.extend([gsocket])
	gsocket.settimeout(20.0)
	gsocket.connect((host, int(port)))
	gsocket.settimeout(None)
	if query!=None:
		query="\t"+query
	else:
		query=""
	if vers==2:
		gsocket.sendall(""+(selector)+query+'\r\n')
	else:
		gsocket.sendall((""+(selector)+query+'\r\n').encode("utf-8"))
	x = gsocket.recv(1024)
	tmpbuff=tempfile.TemporaryFile("r+b")
	while (x) and stopget==0:
		print("Receiving...")
		tmpbuff.write(x)
		x = gsocket.recv(1024)
	if stopget!=0:
		print("Connection to: \"" + host + ":" + str(port) + " " + selector + "\" Terminated early.")
	gsocket.close()
	socketlist.remove(gsocket)
	tmpbuff.seek(0)
	print("done.")
	return tmpbuff


if __name__=="__main__":
	gdat=gopherget("gopher.floodgap.com", 70, "")
	menulist=menudecode(gdat)
	for item in menulist:
		print(item.name)
