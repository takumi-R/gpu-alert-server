import mysql.connector
import os
USERNAME_SQL = os.environ.get("USERNAME_SQL")
PASSWD_SQL = os.environ.get("PASSWD_SQL")
"""
ql> create table pcname( pcid int NOT NULL AUTO_INCREMENT, name text,PRIMARY KEY (pcid));

create table pcgpu( gpuid int NOT NULL AUTO_INCREMENT, pcid int NOT NULL, pcgpuid int NOT NULL,memory int NOT NULL,PRIMARY KEY (gpuid),FOREIGN KEY (pcid) REFERENCES pcname(pcid) );
mysql> create table reserv( reservid int NOT NULL AUTO_INCREMENT, channelid text  NOT NULL,pcid int NOT NULL ,PRIMARY KEY (reservid),FOREIGN KEY (pcid) REFERENCES pcname(pcid) );
create table reservgpu(reservgpuid int NOT NULL AUTO_INCREMENT,reservid int NOT NULL,gpuid int NOT NULL,memory text NOT NULL ,PRIMARY KEY (reservgpuid),FOREIGN KEY (reservid) REFERENCES reserv(reservid),FOREIGN KEY (gpuid) REFERENCES pcgpu(gpuid) );

mysql> create table reservgpu(reservgpuid int NOT NULL AUTO_INCREMENT,reservid int NOT NULL,memory text NOT NULL ,PRIMARY KEY (reservgpuid),FOREIGN KEY (reservid) REFERENCES reserv(reservid) );




"""
class database_set:
    def __init__(self):
       self.config = {
                'user': USERNAME_SQL,
                'password': PASSWD_SQL,
                'host': 'localhost',
                'database' : 'Aquadatabase'
                 }        

       try:
           self.cnx = mysql.connector.connect(**self.config)
           self.cursor = self.cnx.cursor()

       except mysql.connector.Error as err:
           if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
               print('Cannnot connect database.')
           else:
               print(err)



    def set_gpu(self,content):
        add_pc = ("INSERT INTO pcname(name) "
                  "SELECT %s"
                  "where NOT EXISTS (select name from pcname where name=%s)")
        get_pcid = ("SELECT pcid FROM pcname "
                    "where  name = %s")

        get_gpuid = ("SELECT gpuid FROM pcgpu "
                    "where pcid=%s and pcgpuid=%s ")

        check_pc = ("select pcid,pcgpuid,memory from pcgpu WHERE pcid=%s and pcgpuid=%s")


        add_gpu = ("INSERT INTO pcgpu(pcid,pcgpuid,memory) "
                   "VALUES (%s,%s,%s)")
        update_gpu = ("UPDATE pcgpu "
                      "SET pcid=%s,pcgpuid=%s,memory=%s "
                      "WHERE gpuid=%s")


        self.cursor.execute(add_pc,(str(content['name']),str(content['name'])))

        self.cursor.execute(get_pcid,(str(content['name']),))
        pcid = self.cursor.fetchall()

        for gpu_size_i in range(len(content['gpu_size'])):
            self.cursor.execute(check_pc,(pcid[0][0],gpu_size_i))
            if not len(self.cursor.fetchall()):
                self.cursor.execute(add_gpu,(pcid[0][0],gpu_size_i,str(content['gpu_size'][gpu_size_i])))
            else:    
                self.cursor.execute(get_gpuid,(pcid[0][0],gpu_size_i))
                gpuid = self.cursor.fetchall()
                self.cursor.execute(update_gpu,(pcid[0][0],gpu_size_i,str(content['gpu_size'][gpu_size_i]),gpuid[0][0]))



        self.cnx.commit()
    def set_reserv(self,channel_id,pc_id,gpu_mem):
        #create table reservgpu(reservgpuid int NOT NULL AUTO_INCREMENT,reservid int NOT NULL,gpuid int NOT NULL,memory text NOT NULL ,PRIMARY KEY (reservgpuid),FOREIGN KEY (reservid) REFERENCES reserv(reservid),FOREIGN KEY (gpuid) REFERENCES pcgpu(gpuid) );

        add_reserv = ("INSERT INTO reserv(channelid ,pcid) "
                      "VALUES (%s,%s)")

        get_reserv = ("SELECT reservid FROM reserv "
                      "where channelid=%s and pcid=%s ")

        check_reserv = ("select channelid,pcid from reserv WHERE channelid=%s and pcid=%s")
        

        check_reservgpuid = ("select reservgpuid,memory from reservgpu WHERE reservid=%s and gpuid=%s")

        add_reservgpu = ("INSERT INTO reservgpu(reservid,memory,gpuid) "
                             "VALUES (%s,%s,%s)")

        update_reservgpu = ("UPDATE reservgpu "
                            "SET reservid=%s,memory=%s,gpuid=%s "
                            "WHERE reservgpuid=%s")

        get_gpuid  = ("SELECT gpuid from pcgpu "
                      "where pcid=%s and pcgpuid=%s ")

        self.cursor.execute(check_reserv,(channel_id,pc_id))
        if not len(self.cursor.fetchall()):
            self.cursor.execute(add_reserv,(channel_id,pc_id))
        self.cursor.execute(get_reserv,(channel_id,pc_id))
        reservid = self.cursor.fetchall()


        print("gpuid:"+ str(len(gpu_mem)))
        for gpu_size_i in range(len(gpu_mem)):

            self.cursor.execute(get_gpuid,(pc_id,gpu_size_i))
            gpuid = self.cursor.fetchall()
            print(type(reservid[0][0]))
            print(type(gpuid[0][0]))
            print("gpuid:"+ str(gpuid[0][0]))
            print("reservid:"+ str(reservid[0][0]))
            self.cursor.execute(check_reservgpuid,(reservid[0][0],gpuid[0][0]))
            reservgpuid=self.cursor.fetchall()
            print(reservgpuid)
            if not len(check_reservgpuid):
                self.cursor.execute(add_reservgpu,(reservid[0][0],gpu_mem[gpu_size_i],gpuid[0][0]))
            else:    
                self.cursor.execute(update_reservgpu,(reservid[0][0],gpu_mem[gpu_size_i],gpuid[0][0],reservgpuid[0][0]))

        
        self.cnx.commit()
    def check_reserv(self):
        get_reserv_single = ("SELECT DISTINCT reservid  FROM pcgpu "
                            "INNER JOIN reservgpu ON pcgpu.gpuid = reservgpu.gpuid "
                            "WHERE pcgpu.memory <= reservgpu.memory")
        get_reserv_memnum = ("SELECT COUNT(*)  FROM pcgpu "
                             "INNER JOIN reservgpu ON pcgpu.gpuid = reservgpu.gpuid "
                             "WHERE pcgpu.memory <= reservgpu.memory and reservid=%s")

        get_reservnum = ("SELECT COUNT(*)  FROM reservgpu WHERE reservid=%s ")

        del_reservid = ("DELETE  FROM reservgpu WHERE reservid=%s ")
        del_reservid_reserv = ("DELETE  FROM reserv WHERE reservid=%s ")
        get_channelid = ("SELECT channelid,pcid FROM reserv where reservid=%s ")

        channelid_list = []
        self.cursor.execute(get_reserv_single)
        reserv_single = self.cursor.fetchall()
        for reservid in reserv_single:    
            self.cursor.execute(get_reserv_memnum,(reservid[0],))
            reservid_mem_num = self.cursor.fetchall()

            self.cursor.execute(get_reservnum,(reservid[0],))
            reservid_num = self.cursor.fetchall()
            if reservid_mem_num == reservid_num :
                self.cursor.execute(get_channelid,(reservid[0],))
                channelid_list += self.cursor.fetchall()

                     
                self.cursor.execute(del_reservid,(reservid[0],))
                self.cursor.execute(del_reservid_reserv,(reservid[0],))
        self.cnx.commit()
        return channelid_list
    def ls_name(self):
      self.cursor.execute("select * from pcname")
      ls_name = self.cursor.fetchall()
      return ls_name
    def get_gpu_num(self,pc_id):
        self.cursor.execute("SELECT COUNT(*)  FROM pcgpu WHERE pcid=%s",(pc_id,))
        return self.cursor.fetchall()[0][0]

                        













    def __del__(self):
        self.cursor.close()
        self.cnx.close()
    #content['gpu_id']] = { 'size' :content['gpu_size'] , 'mem' : content['gpu_mem'],'name' : content['name'] }







    #   cnx.close()

