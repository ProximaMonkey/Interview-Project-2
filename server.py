#!/usr/bin/python
"""
server.py

Simple HTTP server
"""
import socket
import os
import mimetypes
# had to do this to properly resolve filenames
from urllib import unquote

verbose = False

def generate_directory_index(dir_path):
    s = """<HTML><HEAD><TITLE>Simple HTTP Server</TITLE></HEAD><BODY>
<H1>Directory Contents</H1><H2>%s</H2>""" % dir_path
    for dir_entry in sorted(os.listdir(dir_path)):
        abs_path = os.path.join(dir_path, dir_entry)
        s += '<br><a href="%s">' % abs_path[1:] + dir_entry + "</a>\n"
    s += "</BODY></HTML>\n"
    return s



def generate_HTTP_header(file_path):
    url = "file://%s" % os.path.abspath(file_path)
    content_type = mimetypes.guess_type(url)
    header = ["HTTP/1.1 200 OK"]
    if os.path.isdir(file_path):
        header.append("Content-Type: text/html; charset=utf-8")
    elif content_type[0]:
        header.append("Content-Type: %s" % content_type[0])
        if content_type[1]:
            header[-1] += "; charset=%s" % content_type[1]
    header.append("\r\n")
    if verbose:
        print file_path, header
    return "\r\n".join(header)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 8080))
s.listen(5)


try:
    while True:
        client_socket, address = s.accept()
        data = client_socket.recv(1024)
        
        # throw out bad HTTP requests
        try:
            data_head = data.split("\n", 1)[0].split()
            assert data_head[0] == "GET"
            request = unquote(data_head[1])[1:]
            assert data_head[2] == "HTTP/1.1"
        except:
            continue
        
        if verbose:
            print "request =", request
        file_path = os.path.join(os.curdir, request)
        # only process existing files
        if os.path.exists(file_path):
            client_socket.send(generate_HTTP_header(file_path))
            if os.path.isdir(file_path):
                client_socket.send(generate_directory_index(file_path))
            else:
                client_socket.send(open(file_path).read())
        client_socket.close()
finally:
    s.close()
    print "socket closed"
