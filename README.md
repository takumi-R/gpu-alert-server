# Gpu usage alert slack bot(server)

## INSTALL  
##### Clone the repo

```bash
$ https://github.com/takumi-R/gpu-alert-server.git
$ cd gpu-alert-server
```

##### Create the virtualenv
```bash
$ mkvirtualenv flask
```

##### Install dependencies
```bash
$ pip install -r requirements.txt
```
##### Install SQL server(My SQL)
```bash
$ apt install mysql-server mysql-clientapt  
```
##### Setup SQL server(My SQL)
refer to URL https://qiita.com/houtarou/items/a44ce783d09201fc28f5
##### Create database(My SQL)
```SQL
CREATE DATABASE Aquadatabase;
create table pcname( pcid int NOT NULL AUTO_INCREMENT, name text,PRIMARY KEY (pcid));
create table pcgpu( gpuid int NOT NULL AUTO_INCREMENT, pcid int NOT NULL, pcgpuid int NOT NULL,memory int NOT NULL,PRIMARY KEY (gpuid),FOREIGN KEY (pcid) REFERENCES pcname(pcid) );
create table reserv( reservid int NOT NULL AUTO_INCREMENT, channelid text  NOT NULL,pcid int NOT NULL ,PRIMARY KEY (reservid),FOREIGN KEY (pcid) REFERENCES pcname(pcid) );
create table reservgpu(reservgpuid int NOT NULL AUTO_INCREMENT,reservid int NOT NULL,gpuid int NOT NULL,memory text NOT NULL ,PRIMARY KEY (reservgpuid),FOREIGN KEY (reservid) REFERENCES reserv(reservid),FOREIGN KEY (gpuid) REFERENCES pcgpu(gpuid) );

```
##### Set env in env_server_sample.sh
```bash
$ vim env_server_sample.sh 
```

