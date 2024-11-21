import paramiko
import ast
import mysql.connector
from mysql.connector import Error

command="hostname"
host="192.168.29.152"

username="cdadmin"
password="cdadmin"


local_script_path="C:\\Users\\sbcod\\Desktop\\Study Files\\myFile.py"
client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password)



# Open SFTP session to upload the file to the destination machine's home directory
dest_sftp = client.open_sftp()
dest_file_path = f"/home/cdadmin/mytestnew.py"  # Linux-style home directory path
dest_sftp.put(local_script_path, dest_file_path)  # Upload the file

_stdin, _stdout,_stderr = client.exec_command("python3 mytestnew.py")


def insertPlatfromToDatabse(record1,record2,record3,record4):
    try:
        # Establishing connection to the MySQL database
        connection = mysql.connector.connect(
            host="localhost",  # Update if necessary
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

myresult=_stdout.read().decode()
print(type(myresult))

# Strip any extra whitespace and convert the string output to a tuple using `ast.literal_eval`
tuples = ast.literal_eval(myresult.strip())
print("Received tuples:", tuples)

        # Now you can handle the tuples in Python1
for t in tuples:
    print(f"Tuple: {t}")
            
print(_stdout.read().decode())
r1=tuples[0]
r2=tuples[1]
r3=tuples[2]
r4=tuples[3]

print(_stdout.read().decode())
dest_sftp.close()
client.close()

insertPlatfromToDatabse(r1,r2,r3,r4)
print(r1,r2,r3,r4)
