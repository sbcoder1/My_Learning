import paramiko
import platform
import socket
import psutil
import mysql.connector
from mysql.connector import Error
command="hostname"
host="192.168.29.161"

username="cdadmin"
password="cdadmin"
client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password)

def getPlatform():
    version=platform.version()
    system=platform.system()
    release=platform.release()
    uname=platform.uname().node
    n_node=platform.node()
    machine=platform.machine()
    processor=platform.processor()
    architecture=platform.architecture()[1]

    result1=(version,system,release,uname,n_node,machine,processor,architecture)
    return result1

def cpuInfo():
    pysical_cores=psutil.cpu_count()
    max_freq=psutil.cpu_freq()[2]
    min_freq=psutil.cpu_freq()[1]
    cpu_usage=psutil.cpu_freq()[0]
    cpu_total=psutil.cpu_percent()

    result2=(pysical_cores,max_freq,min_freq,cpu_usage,cpu_total)
    return result2

def memoryInfo():
    partition = psutil.disk_partitions()[0]  
    file_type = partition.fstype
    total_memory=psutil.virtual_memory()[0]
    avaible=psutil.virtual_memory()[1]
    used=psutil.virtual_memory()[3]
    percentage=psutil.virtual_memory()[2]

    result3=(file_type,total_memory,avaible,used,percentage)
    return result3

def networkInfo():
    hostname=platform.node()
    ip_address=socket.gethostbyname(socket.gethostname())
    byte_send=psutil.disk_io_counters()[2]
    byte_receive=psutil.disk_io_counters()[3]

    result4=(hostname,ip_address,byte_send,byte_receive)
    return result4
    
    

def insertPlatfromToDatabse(record1,record2,record3,record4):
    try:
        # Establishing connection to the MySQL database
        connection = mysql.connector.connect(
            host="127.0.0.1",  # Update if necessary
            user="root",  # Replace with your MySQL username
            password="root",  # Replace with your MySQL password
            database="systeminfo"  # Replace with your database name
        )

        cursor = connection.cursor()

             
        # SQL query to insert data
        insert_query1 = """
        INSERT INTO systeminfo.platforminfo (version,system,sys_release,uname,n_node,machine,processor,architecture
        ) VALUES (%s,%s, %s, %s, %s, %s, %s, %s)
        """

        insert_query2 = """
        INSERT INTO systeminfo.cpuinfo (pysical_cores,max_freq,min_freq,cpu_usage,cpu_total
        ) VALUES (%s,%s, %s, %s, %s)
        """

        insert_query3 = """
        INSERT INTO systeminfo.memoryinfo (file_type,total_memory,avaible,used,percentage
        ) VALUES (%s,%s, %s, %s, %s)
        """

        insert_query4 = """
        INSERT INTO systeminfo.networkinfo (hostname,ip_address,byte_send,byte_receive
        ) VALUES (%s,%s, %s, %s)
        """
        
        print(insert_query1,record1)
        print(insert_query2,record2)
        print(insert_query3,record3)
        print(insert_query4,record4)
        
        # Executing the query
        cursor.execute(insert_query1, record1)
        cursor.execute(insert_query2, record2)
        cursor.execute(insert_query3, record3)
        cursor.execute(insert_query4, record4)
        connection.commit()

        print(f"Data inserted succesfully")

    except Error as e:
        print(f"Error inserting data: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection.is_connected():
            connection.close()
            print("MySQL connection closed.")


    
print(getPlatform())
print(cpuInfo())
print(memoryInfo())
print(networkInfo())

myrecord1 = getPlatform()
myrecord2 = cpuInfo()
myrecord3 = memoryInfo()
myrecord4 = networkInfo()

insertPlatfromToDatabse(myrecord1, myrecord2, myrecord3, myrecord4)


_stdin, _stdout,_stderr = client.exec_command("python3 dataCollections.py")
print(_stdout.read().decode())
