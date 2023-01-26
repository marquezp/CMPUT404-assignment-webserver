#  coding: utf-8 
import socketserver
from os import path

# Copyright 2023 Abram Hindle, Eddie Antonio Santos, Jorge Marquez Peralta
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    # checks for any backwards paths ../../
    def check_backwards(self, path_to_file):
        return (".." in (path_to_file.split("/")))

    # is the file valid
    def does_file_exist(self, path_to_file):
        return (path.exists("./www"+ path_to_file))

    # returns the file extension type
    def get_content_type(self, path_to_file):
        try:
            file_type = path_to_file.split(".")[1]
        except:
            return None
        match file_type:
            case "css":
                content_type = "text/css; charset=utf-8\r\n"
            case "html":
                content_type = "text/html; charset=utf-8\r\n"

        return content_type
    
    # returns the content of the file in the given path
    def get_content(self, path_to_file):
        return open("./www" + path_to_file,"r").read()

    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        # get the HTTP method, protocol version, and path for the request
        status_line = self.data.decode('utf-8').split("\r\n")[0]
        method, path_to_file, version = status_line.split(" ")

        # only accept GET requests
        if method == "GET":
            if self.does_file_exist(path_to_file) and not self.check_backwards(path_to_file):
                # get file type and content
                response = version + " 200 OK\r\n"
                content_type = self.get_content_type(path_to_file)
                # handle request according to wether its a file or directory
                if content_type != None: # path lead to a file
                    content = self.get_content(path_to_file)
                else: # path lead to a directory
                    # check for 301
                    if path_to_file[-1] != "/": 
                        # redirect to path + '/'
                        response = version + " 301 Moved Permanently\r\n"
                        response += "Location: " + path_to_file + "/\r\n"
                    # serve the index.html of that directory
                    content_type = "text/html; charset=utf-8\r\n"
                    content = self.get_content(path_to_file+"/index.html")
                # append the rest of the http headers
                response += "Connection: Close\r\n"
                response += "Content-Length: " + str(len(content)) + "\r\n"
                response += "Content-Type: " + content_type + "\r\n"
                response += "\r\n\n" + content
                self.request.sendall(bytearray(response,'utf-8'))

            else: # 404 file doesnt exist
                response = version + " 404 Not Found\r\n"
                self.request.sendall(bytearray(response,'utf-8'))
                return
        else: # not a GET request, serve a 405
            response = version + " 405 Method Not Allowed\r\n"
            self.request.sendall(bytearray(response,'utf-8'))
            return

    

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
