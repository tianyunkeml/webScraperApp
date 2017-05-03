#! /usr/bin/python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import re
import pdb
import chardet
import sys
import wx
import smtplib  
from email.mime.text import MIMEText

reload(sys)
sys.setdefaultencoding('utf-8')

class myScaper(object):
	def __init__(self, url):
		self.url = url

	def getContent(self):
		headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'}
		r = requests.get(self.url, headers = headers)
		return r.text

	def analyzeKeyword(self, keywords):
		while '（' in keywords or '）' in keywords or '，' in keywords:
			keywords = keywords.replace('（', '(').replace('）', ')').replace('，', ',')
		kwList = keywords.strip().split('|')
		result = []
		for section in kwList:
			section = [wd.strip() for wd in section.strip().strip('(').strip(')').strip().split(',')]
			result.append(section)
		return result

	def findNews(self, keywords):
		def allInString(kw, string):
			return reduce(lambda x, y: x and y, [w in string for w in kw])

		def getChineseChar(string):
			if '.sina.' in self.url:
				return string.encode('raw_unicode_escape')
			if '.qq.' in self.url:
				return string
			if '.163.' in self.url:
				return string

		kwList = self.analyzeKeyword(keywords)
		soup = BeautifulSoup(self.getContent(), 'html.parser')
		result = soup.find_all('a')
		newsList = []
		for r in result:
			# pdb.set_trace()
			if r.string != None and reduce(lambda x, y: x or y, [allInString(kw, getChineseChar(r.string)) for kw in kwList]):
				# print r.string.encode('raw_unicode_escape')
				link = r['href']
				title = getChineseChar(r.string)
				newsList.append(title + ': ' + link)
				print title + ': ' + link
		return newsList

class myGUI(object):
	def __init__(self):
		def resize(size):
			return int(size * 1.2)
		self.app = wx.App()
		self.window = wx.Frame(None, title = 'News Sniffer', size = (resize(800), resize(600)))


	def layout(self):
		def resize(size):
			return int(size * 1.2)

		with open('configs.txt', 'r') as f:
			defaultVal = f.read().split('\n***\n')

		app = self.app
		window = self.window
		
		panel = wx.Panel(window)

		urlLabel = wx.StaticText(panel, -1, "Websites to Search", pos = (resize(30), resize(15)))
		self.urlText = wx.TextCtrl(panel, -1,  
			defaultVal[0], 
			size=(resize(350), resize(180)), pos = (resize(30), resize(35)), style=wx.TE_MULTILINE) #创建一个文本控件  
		self.urlText.SetInsertionPoint(0) #设置插入点  

		resultLabel = wx.StaticText(panel, -1, "Results", pos = (resize(120), resize(305)))  
		self.resultText = wx.TextCtrl(panel, -1,   
			"",  
			size=(resize(560), resize(230)), pos = (resize(120), resize(330)), style=wx.TE_MULTILINE|wx.TE_RICH2) #创建丰富文本控件  
		self.resultText.SetInsertionPoint(0)  
		# richText.SetStyle(44, 52, wx.TextAttr("white", "black")) #设置文本样式  
		# points = richText.GetFont().GetPointSize()   

		# f = wx.Font(points + 3, wx.ROMAN, wx.ITALIC, wx.BOLD, True) #创建一个字体  
		# richText.SetStyle(68, 82, wx.TextAttr("blue", wx.NullColour, f)) #用新字体设置样式  
		# sizer = wx.FlexGridSizer(cols=2, hgap=6, vgap=6)  
		# sizer.AddMany([multiLabel, multiText, richLabel, richText])

		self.kwText = wx.TextCtrl(panel, -1,  
			defaultVal[1], 
			size=(resize(300), resize(20)), pos = (resize(200), resize(260)))
		self.kwText.SetInsertionPoint(0)
		goButton = wx.Button(panel, -1, 'Go', pos = (resize(515), resize(255)), size = (resize(50), resize(30)))

		# histButton = wx.Button(panel, -1, 'History', pos = (resize(580), resize(300)), size = (resize(100), resize(30)))

		pushLabel = wx.StaticText(panel, -1, "Email Address", pos = (resize(500), resize(50)))
		self.pushText = wx.TextCtrl(panel, -1,  
			defaultVal[2], 
			size=(resize(150), resize(20)), pos = (resize(580), resize(50))) #创建一个文本控件  
		self.pushText.SetInsertionPoint(0) #设置插入点  

		periodLabel = wx.StaticText(panel, -1, "Period (hours)", pos = (resize(500), resize(150)))
		self.periodText = wx.TextCtrl(panel, -1,  
			defaultVal[3], 
			size=(resize(150), resize(20)), pos = (resize(580), resize(150))) #创建一个文本控件  
		self.periodText.SetInsertionPoint(0) #设置插入点  


		# Event Settings
		# urlSet = urlText.GetValue()
		# keywords = kwText.GetValue()
		# address = pushText.GetValue()
		# period = periodText.GetValue()

		window.Bind(wx.EVT_BUTTON, self.go)
		# result = go(urlSet, keywords)
		


		window.Center()
		window.Show(True)
		app.MainLoop()

	def go(self, e):

		def send(address, result):
			if '@' in address:
				mailto_list = [address] 
				mail_host = "smtp.gmail.com"
				mail_user = "newsSnifferMail"
				mail_pass = "Ilove6ml!"
				mail_postfix = "gmail.com"
				mail_subject = "News Push!"
				content = 'Dear User:\nThe up to date news:\n' + reduce(lambda x, y: x + '\n' + y, result)
				msg = MIMEText(content,_subtype='plain',_charset='gb2312')
				msg['Subject'] = mail_subject
				msg['From'] = "<"+mail_user+"@"+mail_postfix+">"
				msg['To'] = ";".join(mailto_list)
				try:  
					server = smtplib.SMTP()  
					server.connect(mail_host, 587)  
					server.starttls()
					server.login(mail_user, mail_pass)  
					server.sendmail(msg['From'], mailto_list, msg.as_string())  
					server.close()  
				except Exception, e:  
					print str(e)  


		urlSet = self.urlText.GetValue()
		keywords = self.kwText.GetValue().encode('utf-8')
		address = self.pushText.GetValue()
		period = self.periodText.GetValue()

		with open('configs.txt', 'w') as f:
			f.write(urlSet + '\n***\n' + keywords + '\n***\n' + address + '\n***\n' + period)

		urlSet = str(urlSet).strip().split('\n')
		print urlSet
		result = []
		for url in urlSet:
			if len(url) == 0:
				continue
			try:
				scraper = myScaper(url)
			except:
				print 'error with url'
			result.extend(scraper.findNews(keywords))
			print result
		if len(result) == 0:
			output = ''
		elif len(result) == 1:
			output = result[0]
		else:
			output = reduce(lambda x, y: x + '\n' + y, result)
		self.resultText.SetValue(output)
		send(address, result)







if __name__ == '__main__':
	# scraper1 = myScaper('http://news.163.com/')
	# kw = '(习近平)|(川普,要让)'
	# scraper1.findNews(kw)
	gui = myGUI()
	gui.layout()