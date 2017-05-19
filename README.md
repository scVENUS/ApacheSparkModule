# scVENUS Apache Spark Module

## Packaging

* logon to a scVENUS client or place a copy of scpm in your $PATH for creating the spark and java packages

* create spark package(s)

    This task downloads spark-2.0.2-bin-hadoop2.7.tgz and spark-2.1.0-bin-hadoop2.7.tgz and generates p4 packages bin build/spark*.p4

    ```shell
    ./gradlew p4Sparks
    ```

* create zulu java package

    Downloads jdk8.0.112 from Azul Systems and generates a p4  package build/zulu8.19.0.1-jdk8.0.112-linux_x64.p4

    ```shell
    ./gradlew p4Javas
    ```

* create the anacoda package
    The anaconda software has a more complex installer and therefore has to be installed on a test / build machine and then repackaged as p4.
    Download and install anacoda3 once on a build machine and create a p4 package by executing
    ```shell
    cd /usr/local
    scpm -c -n anaconda  -p anaconda.p4  -s anaconda3  -v "3-4.2.0"  --dest-prefix=/usr/local   --default-owner="ADMUID=0"  --default-group="ADMGID=10000"
    ```

* create the meta package
    Adapt the path to the anaconda p4 package which you have created in the previous step in the filelist src/main/resources/filelists/spark-venus.f4 and then execute:
    ```shell
    ./gradlew createMetaPackage
    ```

* You can get a listing of all available gradle targets with `./gradlew -q tasks -all`



## Installation using the meta package

* install / update domain tree

```bash
scmetadoall -c --dont-merge --move-sw --cleanup spark-venus-meta.p4
```

* add software to sw-depot

```bash
for i in software_deliver/spark/*.p4; do echo $i ; done
```

## Spark / Jupiter Method Documentation

### Spark

#### Spark ConfDepot Artifacts

* method and context sc.venus.spark
* files
  * systemd template: /etc/systemd/system/scvenus-spark.service
  * spark-env.sh template: /usr/local/etc/spark/spark-env.sh
  * spark-defaults.conf template: /usr/local/etc/spark-defaults.conf

#### sc.venus.spark Install Mode

* installs spark-hadoop2.7 and zulu-java
* spark software is in /usr/local/spark
* java software goes to /usr/local/zulu-java
* spark configuration is in /usr/local/etc/spark
* creates spark-defaults.conf and spark-env.sh
* spark logs are in /var/log/spark
* spark pids are in /var/run/spark
* creates scvenus-spark systemd unit
* adds scvenus-spark service to systemd startup
* (re)starts the spark service
* the spark service is running as user ${USER} (from context sc.venus.spark)

#### sc.venus.spark Uninstall Mode

* stops the spark service
* removes spark service from systemd startup
* removes scvenus-spark systemd unit
* removes the p4 software spark-hadoop27 and zulu-java
* removes directories /usr/local/etc/spark, /var/run/spark, /var/log/spark

### Jupyter

#### Jupyter ConfDepot Artifacts

* method and context sc.venus.jupyter
* files
  * systemd template: /etc/systemd/system/scvenus-jupyter.service
  * jupyter start wrapper template: /usr/local/bin/scvenus-jupyter

#### sc.venus.jupyter Install Mode

* install anaconda p4 package
* anacoda is in /usr/local/anaconda3
* creates a jupyter start wrapper /usr/local/bin/scvenus-jupiter
* creates scvenus-jupyter systemd unit
* adds scvenus-jupyter to systemd startup
* (re)starts the jupyter service
* the jupyter service is running as user ${USER} (from context sc.venus.spark) 

#### sc.venus.jupyter Uninstall Mode

* stops scvenus-jupyter service
* removes jupyter service from systemd startup
* removes anaconda p4
* removes /usr/local/bin/scvenus-jupyter

## Spark Example Setup

### Description

The spark and jupyter methods only support OSes using systemd: go for __redhatel 7__.

The setup relies on the scVENUS single system image. Make sure SSI is working.

The p4 packages spark-hadoop2.7, zulu-java and anaconda must be added to the scVENUS software depot.

The spark processes are owned by the user "scvenusSpark".

The jupyter notebook is owned by the user "scvenusSpark" and is running on the spark master.

The shared directory for spark is /home/scvenusSpark.

A hierachical group structure for the cluster members: sparkcluster1/master, sparkcluster1/slave

The spark master configuration is in "groups/sparkcluster1/master/context/sc.venus.spark".

The spark slave configuration is in "groups/sparkcluster1/slave/context/sc.venus.spark".

The share cluster configuration is in "groups/sparkcluster1/context/sc.venus.spark".

The spark master is client4 (client4.example.com).

The spark slaves are client6 and client9.

### Setup

* add a user which is the owner of the spark process and its home directory is used as shared storage for the spark cluster

    ```shell
    scadduser -s /usr/local/bin/bash -h client4 -u scvenusSpark
    ```

* add a venus group for the spark slaves and add clients to the group.

    ```shell
    scaddvenusgroup -c sparkcluster1/master
    scchclient -c +g sparkcluster1/master client4
    scaddvenusgroup -c sparkcluster1/slave
    scchclient -c +g sparkcluster1/slave client6
    scchclient -c +g sparkcluster1/slave client9
    ```

* add venus context settings

    ```shell
    sccontextchange -c domain/groups/sparkcluster1/master/context/sc.venus.spark NODE_TYPE MASTER
    sccontextchange -c domain/groups/sparkcluster1/context/sc.venus.spark AUTHENTICATE true
    sccontextchange -c domain/groups/sparkcluster1/context/sc.venus.spark SECRET 'veryS3cret!'
    sccontextchange -c domain/groups/sparkcluster1/context/sc.venus.spark USER scvenusSpark
    sccontextchange -c domain/groups/sparkcluster1/context/sc.venus.spark WORKING_DIR /home/scvenusSpark
    sccontextchange -c domain/groups/sparkcluster1/context/sc.venus.spark SPARK_WORKER_DIR /home/scvenusSpark/work
    sccontextchange -c domain/groups/sparkcluster1/context/sc.venus.spark SPARK_EVENT_LOG_DIR_PATH /home/scvenusSpark/event-log
    sccontextchange -c domain/groups/sparkcluster1/context/sc.venus.spark CREATE_EVENT_LOG_DIR true
    sccontextchange -c domain/groups/sparkcluster1/context/sc.venus.spark MASTER_URL_HOST client4.example.com
    # slave settings
    sccontextchange -c domain/groups/sparkcluster1/slave/context/sc.venus.spark NODE_TYPE SLAVE
    ```

* add jupyter password to context settings

  * generate the password hash with the password hash generator script from this project

    ```bash
    ./src/main/resources/bin/scjupyter-passwd.py
    ```

  * add the hashed password to the jupyter context

    ```shell
        sccontextchange -c domain/groups/sparkcluster1/master/context/sc.venus.jupyter NOTEBOOK_PASSWORD_HASH 'sha1:aeee03cb33c0:0e4d047e13e3f853b775c6df15baf0ce329489d0'
    ```

* optionally choose a spark version

    available versions are: 2.1.0, 2.0.2
    ```bash
    sccontextchange -c domain/groups/sparkcluster1/context/sc.venus.spark spark_version 2.0.2
    ```

* install and start the spark master and slaves

    ```shell
    scrinstall -c sc.venus.spark sparkcluster1
    ```

* install the jupyter software on all spark slaves

    ```shell
    scaddpkg -c anaconda sparkcluster1/slave
    ```

* install and start the jupyter notebook

    ```shell
    scrinstall -c sc.venus.jupyter sparkcluster1/master
    ```

## Web interfaces

* Web interface Spark  <http://masterhost:8080>
* Web interface Jupyter <http//masterhost:8888>

## Dev Links

* Example Notebook: <http://blog.insightdatalabs.com/jupyter-on-apache-spark-step-by-step/>

* jupyterhub?
    <https://github.com/jupyterhub/jupyterhub/wiki/Run-jupyterhub-as-a-system-service>
