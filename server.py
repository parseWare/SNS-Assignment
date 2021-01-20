import socket  # Last Updated Jan 21 1:16 am
import select
import sys
import threading

host="127.0.0.1"
port=7004

conn_clients=[]
client_port={}
logged_in={}

class ward:
    clientidpass = {}
    active_groups={}


obj = ward

def login(conn, addr, id , passw, cli_port):
    #print(obj.clientidpass)
    if id in obj.clientidpass:
        if(obj.clientidpass[id]==passw):
            logged_in[id]=cli_port
    
            conn.send(("Logged in successfully;1").encode())
        else:
            conn.send(("password incorrect;0").encode())
    else:
        conn.send(("Not a registered User;0").encode())

def signup(conn, addr, id , passw):
    if id not in obj.clientidpass:
        obj.clientidpass[id]=passw
        conn.send(("successfully signed in").encode())
    else:
        conn.send(("Username Already Exists").encode())


def detctdata(conn ,addr, strn):
    mylst = strn.split(";")
    if(mylst[0]=="login"):
        id = mylst[1]
        passw = mylst[2]
        login(conn, addr, id, passw, mylst[3])

    elif(mylst[0]=="signup"):
        id = mylst[1]
        passw = mylst[2]
        signup(conn,addr, id, passw)

    elif(mylst[0]=="port"):
        username=mylst[1]
        if username not in obj.clientidpass:
            if username not in obj.active_groups:
                s="this user/group doesn't exists;0"
            else:
                s=""
                for usr in obj.active_groups[username]:
                    s+=logged_in[usr]+";"
                s+="1G"
            conn.sendall(s.encode())
        elif username not in logged_in:
            conn.send(("this user is not logged in;0").encode())
        else:
            s=logged_in[username]+";1"
            conn.send(s.encode())

    elif(mylst[0]=="create"):
        if mylst[1] in obj.active_groups:
            s="group is already present"
        else:
            obj.active_groups[mylst[1]]=[]
            obj.active_groups[mylst[1]].append(mylst[2])
            s="group created successfully"
        conn.sendall(s.encode())

    elif(mylst[0]=="join"):
        if mylst[1] not in obj.active_groups:
            obj.active_groups[mylst[1]]=[]
            obj.active_groups[mylst[1]].append(mylst[2])
            s="group created and joined successfully"
        else:
            obj.active_groups[mylst[1]].append(mylst[2])
            s="group joined successfully"
        conn.sendall(s.encode())

    elif(mylst[0]=="list"):
        s=""
        for grp in obj.active_groups:
            s+=grp+" "+str(len(obj.active_groups[grp]))+";"
        conn.sendall(s.encode())

def new_client(conn,addr):
    while True:
        data=conn.recv(1024)
        if data:
            #print(data.decode())
            detctdata(conn,addr, data.decode())
        else:
            continue

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    s.bind((host,port))

    s.listen() 
    while True:
    
        conn,addr=s.accept()
        conn_clients.append(conn)
        
        #print(conn)
        print('Connected to ',addr)

        t1=threading.Thread(target=new_client,args=(conn,addr))
        
        t1.start()