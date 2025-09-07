# TLS client-server socket connection

## About the project

This is a coursework assignment, which is why the code is commented in Spanish. Other unusual practices, such as establishing a single connection for each communication with the server, are requirements of the project.

## Why TLS 1.3

TLS 1.3 is the latest version of the TLS protocol. TLS, which is used by HTTPS and other network protocols for encryption, is the modern version of SSL. TLS 1.3 dropped support for older, less secure cryptographic features, and it sped up TLS handshakes, among other improvements.

In a nutshell, TLS 1.3 is faster and more secure than TLS 1.2. One of the changes that makes TLS 1.3 faster is an update to the way a TLS handshake works: TLS handshakes in TLS 1.3 only require one round trip (or back-and-forth communication) instead of two, shortening the process by a few milliseconds. And in cases when the client has connected to a website before, the TLS handshake will have zero round trips. This makes HTTPS connections faster, cutting down latency and improving the overall user experience.

Many of the major vulnerabilities in TLS 1.2 had to do with older cryptographic algorithms that were still supported. TLS 1.3 drops support for these vulnerable cryptographic algorithms, and as a result it is less vulnerable to cyber attacks.

### About TLS

TLS (Transport Layer Security) is the protocol that secures most communication on the internet. It ensures that when two parties (for example, your browser and a website) exchange data, that data is private, authentic, and cannot be modified by attackers.

TLS uses a handshake protocol to establish a secure connection. The handshake begins with the client initiating the process by sending a ClientHello message. Upon receiving ClientHello, the server responds with ServerHello.

Following initial contact, the client and server exchange certificates and parameters to agree on encryption for future messages. This communication ends with ServerFinished and ClientFinished messages. From here on, all data transmitted between the client and the server is encrypted using session keys.

An optional feature in TLS 1.3 is zero round trip time (0-RTT) data. If the client has a preshared key from a previous session, it can send 0-RTT data along with ClientHello to send application data immediately, reducing latency. However, the server processes 0-RTT data only if it accepts the pre-shared key (PSK), and this feature comes with some security tradeoffs, such as the potential for replay attacks.

If you are interested in the topic, research about the TLS Protocol and the handshake process.

## Installation

### 1. Virtual Environment
#### 1.1 Create the virtual environment
```bash
python3 -m venv venv
```
#### Activate the virtual environment
On linux: 
```bash
source venv/bin/activate  
```
On Windows: 

```bash
venv\Scripts\activate
```

#### 1.2 Install virtual environmnt dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MariaDB
#### 2.1 On Ubuntu
```bash
sudo apt install mariadb-server -y
sudo systemctl start mariadb
sudo mysql_secure_installation
```
Values to enter after running the `mysql_secure_installation` command:
```bash
- Enter current password for root (enter for none): (enter)
- Switch to unix_socket authentication [Y/n]: `y`
- Change the root password? [Y/n]: `y`
    - New password: <tu_contraseña_de_root>
    - Re-enter new password: <tu_contraseña_de_root>
- Remove anonymous users? [Y/n]: `y`
- Disallow root login remotely? [Y/n]: `y` 
- Remove test database and access to it? [Y/n]: `y`
- Reload privilege tables now? [Y/n] : `y`
```
Next, to continue with the databas creation:
```bash
sudo mariadb -u root -p
```
Use the root password that you configured earlier. Once inside the MariaDB console, run the following command to create the databases:
```sql
source resources/database.sql;
```

#### 2.2 On Windows
Download MariaDB from the official website and configure the root superuser during installation. Then, open a terminal in the project’s base directory and run the following command:
```bash
mariadb -u root -p
```
Note: If the mariadb command is not recognized, add the MariaDB installation path to the system PATH.

(Optional but recommended) If you want to perform a secure installation like on Ubuntu, run the following SQL statements:
```sql
DELETE FROM mysql.user WHERE User='';
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
FLUSH PRIVILEGES;
```	
To create the databases, run the following command:
```sql
source resources/database.sql;
```
