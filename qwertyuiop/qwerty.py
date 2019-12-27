from flask import Flask, render_template, request, jsonify
from html5print import CSSBeautifier
from bs4 import BeautifulSoup as bs
from requests import get
import requests
import os 
import webbrowser
import shutil
import json 
import urllib3

webserver = Flask(__name__)

sep = '/'
final = ""
myString = ""
newString = ""
link = "./templates/result.html"
test = "./templates/test.html"
domain = "http://localhost:5055/"
html = """
<html>
<head>
<title>Test Page</title>
</head>
<body>
<div>test</div>
</html>
"""


@webserver.route("/")
def home():
    return render_template("index.html"), 200

@webserver.route('/get', methods=['POST'])
def go():
    myString = request.form['ecid']

    try:
        try:
            r = requests.get(myString)
        except requests.ConnectionError:
            errorString = "Your supposed to input a valid url..."
            sHelp = "* couldn't render *"
            return render_template("error.html", error=errorString, help=sHelp), 200
        txt = r.text
        
        newTxt = txt.replace('%','')

        ar = myString.split(sep, 3)
        newAr = [ar[0], ar[1], ar[2]]
        newString = sep.join(newAr)

        writeHtml(newString, newTxt)
        
        return render_template("result.html"), 200

    except Exception:
        return render_template("error.html", error="Hey mate, your supposed to input a url...", help="* https://idiot.com *"), 200

@webserver.route('/get', defaults={'path': ''})
@webserver.route('/get/<path:path>')
def proxy(path):
    try:
        r = requests.get(path)
        txt = r.text
        
        newTxt = txt.replace('%','')

        ar = path.split(sep, 3)
        newAr = [ar[0], ar[1], ar[2]]
        newString = sep.join(newAr)

        writeHtml(newString, newTxt)

        return render_template("result.html"), 200
    except Exception:
        return render_template("error.html", error="Sorry, but uhh this server cannot render that...", help="* :( *"), 200

@webserver.route('/css', defaults={'path': ''})
@webserver.route("/css/<path:path>")
def getCSS(path):

    r = requests.get(path)
    txt = r.text

    final = CSSBeautifier.beautify(txt, 4)

    s = final.encode('utf-8', 'ignore')
    with open(test, 'wb') as f:
        f.write(s)
        f.close

    return render_template("test.html"), 200

@webserver.route('/js', defaults={'path': ''})
@webserver.route("/js/<path:path>")
def getJS(path): 
     return render_template("error.html", error=path, help="lololol"), 200

def links(method, mType, arg, location, soup):
    List = []
    link = soup.find_all(method, {mType : arg})
    for l in link:
        tmp = l.get(location)
        List.append(tmp)
    
    emptyList = list(filter(None, List))
    newList = list(set(emptyList))
    
    return newList

def recycle(path, finalHtml):
    n = 0
    parentString = '"' + domain + path + '/'
    childString = domain + path + '/'

    replaceString = parentString
    while n <= 100:
        replaceString += childString
        finalHtml = finalHtml.replace(replaceString, parentString)
        n += 1
    
    finalHtml = finalHtml.replace(parentString + childString, parentString)
    return finalHtml

def inputStatics(List, urlPath, html):
    for l in List:
        html = html.replace(l, domain + urlPath + '/' + l)
    
    html = recycle(urlPath, html)

    return html

def inputURL(html, List, url):
    while True:
        try:
            List.remove(url+'/')
        except ValueError:
            break

    for i in List:
        html = html.replace(i, 'http://localhost:5055/get/'+i)
    
    html = recycle("get", html)
    return html

def writeHtml(nString, txt):
    txt = txt.replace('"//', '"https://')
    txt = txt.replace("'/", "'"+nString+'/')
    html = txt.replace('"/', '"'+nString+'/')

    soup = bs(html, 'html.parser')

    urlList = links('a', "rel", "", 'href', soup)
    jsList = links('script', "", "", 'src', soup)
    cssList = links('link', "rel", "stylesheet", 'href', soup)

    html = inputURL(html, urlList, nString)
    inputHtml = inputStatics(jsList, "js", html)
    finalHtml = inputStatics(cssList, "css", inputHtml)

    s = finalHtml.encode('utf-8', 'ignore')
    with open(link, 'wb') as f:
        f.write(s)
        f.close

if (__name__ == "__main__"):
    webserver.run(debug=True, port=5055, host='0.0.0.0')
