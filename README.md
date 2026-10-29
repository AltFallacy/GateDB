# GateDB — Secure SQL Governance Gateway & Cloud Database Client

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.0-lightgrey.svg?logo=flask)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![AWS](https://img.shields.io/badge/Cloud-AWS%20EC2%20%7C%20ALB%20%7C%20ASG-orange.svg?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**GateDB** is an enterprise-grade, standalone web SQL governance gateway and multi-engine database client. Designed with a dual-threat architecture, GateDB serves both as a **centralized query-approval firewall** for engineering teams and as a **lightweight, dark-mode personal SQL client** for individual developers.

GateDB bridges the gap between high-security production database access and frictionless local development, eliminating the need to distribute sensitive database passwords across an organization while shielding critical infrastructure behind role-based approval pipelines.

---

## 📑 Table of Contents
- [Why GateDB? (The Core Problem)](#-why-gatedb-the-core-problem)
- [Architecture & Dual-Mode Engine](#-architecture--dual-mode-engine)
  - [1. Admin Central (Governance & Approval Gateway)](#1-admin-central-governance--approval-gateway)
  - [2. My Personal (Direct Developer SQL Client)](#2-my-personal-direct-developer-sql-client)
- [Cloud & DevOps Architecture (AWS)](#-cloud--devops-architecture-aws)
  - [Infrastructure Diagram](#infrastructure-diagram)
  - [AWS Cloud Components](#aws-cloud-components)
- [What GateDB Can Be Used For](#-what-gatedb-can-be-used-for)
- [Experimental Labs & Hands-On Scenarios](#-experimental-labs--hands-on-scenarios)
- [Supported Database Engines](#-supported-database-engines)
- [Getting Started & Installation](#-getting-started--installation)
  - [Option 1: Docker (Recommended)](#option-1-docker-recommended)
  - [Option 2: AWS EC2 Cloud Deployment](#option-2-aws-ec2-cloud-deployment)
  - [Option 3: Local Python Environment](#option-3-local-python-environment)
- [Configuration & Environment Variables](#-configuration--environment-variables)
- [Project Directory Structure](#-project-directory-structure)
- [Security Model & Engineering Highlights](#-security-model--engineering-highlights)

---

## 🎯 Why GateDB? (The Core Problem)

In traditional software teams and university labs, developers often face one of two extremes:
1. **The Security Vulnerability:** Direct database credentials (`root`, passwords, connection strings) are shared over Slack or hardcoded into `.env` files. Junior engineers or contractors have raw access, making accidental `DROP TABLE`, unindexed scans, or unauthorized data exfiltration a major risk.
2. **The Operational Bottleneck:** Developers have zero access and must open Jira tickets for senior DBAs to run simple `SELECT` queries, slowing down debugging and feature delivery.

**GateDB solves both problems:**
* **Zero Shared Credentials:** Standard users write and test queries in the web UI. GateDB executes approved queries on the backend without ever showing the database credentials to the user.
* **Controlled Self-Service:** Developers submit queries to a queue; Admins review the query text with one click; upon approval, GateDB executes the query and returns the tabular result directly to the requester's dashboard.

---

## 🏛 Architecture & Dual-Mode Engine

```
                             [ GateDB Web Portal ]
                                       │
                      Select Environment Target
                                       │
               ┌───────────────────────┴───────────────────────┐
               ▼                                               ▼
      [ Admin Central ]                                [ My Personal ]
 (Governance Approval Required)                 (Direct Personal Execution)
               │                                               │
               ▼                                               ▼
      [ SQLite Queue ]                                [ User's Settings ]
   (pending_req.db)                                 (user_settings.db)
               │                                               │
               ▼                                               ▼
     Admin Reviews & Approves                        Instant Execution on
               │                                      Local/Remote DB
               ▼                                               │
      Backend DB Connectors                                    ▼
   (MySQL / PostgreSQL / SQLite)                     Results Returned to UI
```

### 1. Admin Central (Governance & Approval Gateway)
* **Approval Queue:** All queries targeting central shared infrastructure are stored in `pending_req.db` with a status of `pending`.
* **Central Admin Review:** Administrators access `/querybox` to inspect pending SQL statements, review timestamps and requester IDs, and approve or reject queries individually or in batches.
* **Execution Middleman:** Approved queries are executed by backend database connector classes (`mysql_conns`, `postgres_conns`, `sq3_conns`), capturing raw results or syntax errors safely.
* **Audit Trail:** Users view historical execution outputs, execution timestamps, and approval notes in their `/my-requests` portal.

### 2. My Personal (Direct Developer SQL Client)
* **Instant Bypass:** Developers working against their local sandbox, staging DB, or Docker containers bypass the approval queue entirely.
* **Encrypted Credentials Hub:** Users store connection parameters (host, port, user, password, DB name) in `/settings`.
* **Zero Desktop Bloat:** Acts as a lightweight, dark-mode alternative to resource-heavy desktop GUI clients like DBeaver, PGAdmin, or MySQL Workbench.

---

## ☁ Cloud & DevOps Architecture (AWS)

GateDB is fully containerized and production-ready for deployment on **Amazon Web Services (AWS)** adhering to the AWS Well-Architected Framework:

### Infrastructure Diagram
```
                     [ Internet Users / Clients ]
                                  │
                                  ▼
                      [ Internet Gateway (IGW) ]
                                  │
                                  ▼
               [ Application Load Balancer (ALB) ]
                     (Multi-AZ Public Subnets)
                                  │
                     Target Group: /health Check
                                  │
              ┌───────────────────┴───────────────────┐
              ▼                                       ▼
  [ EC2: gatedb-server ]                  [ Auto Scaling Group ]
   - Ubuntu 24.04 / t2.micro               - Launch Template + AMI
   - Waitress WSGI (0.0.0.0:5000)          - Auto-healing & Scale
   - Docker: -p 80:5000                    - Target Tracking Policy
              │
              ▼
   [ Persistent EBS Mount ] ◄──────────► [ CloudWatch Monitoring ]
     ~/gatedb_data -> /app/data           CPUUtilization > 70% Alarm
     (auth.db, pending_req.db)
```
*(An interactive XML flow diagram is available at [`deployment_flow_diagram.xml`](deployment_flow_diagram.xml) for import into Draw.io / diagrams.net).*

### AWS Cloud Components
* **Compute (Amazon EC2):** Containerized Python 3.12 application served with multi-threaded Waitress WSGI on `t2.micro` (100% Free Tier compliant).
* **Networking & High Availability (ALB + IGW):** Multi-Availability Zone Application Load Balancer distributes HTTP traffic and handles target health verification via `/health`.
* **Scalability & Self-Healing (Auto Scaling Group):** Auto Scaling Group monitors instance health. If an EC2 instance crashes, the ASG automatically terminates and replaces it using pre-baked AMIs.
* **Monitoring & Telemetry (Amazon CloudWatch):** CloudWatch alarms monitor `CPUUtilization`, alerting operators or triggering scaling actions when load exceeds 70%.
* **Persistent Storage (Amazon EBS):** Solves the ephemeral container dilemma by bind-mounting host directory `~/gatedb_data` into `/app/data`, guaranteeing zero data loss across container recreations.
* **Security Shield (Layered Security Groups):** Backend EC2 instances reject direct public web traffic; Port 80 only accepts traffic forwarded from the ALB's security group (`gatedb-alb-sg`).

---

## 💡 What GateDB Can Be Used For

1. **Enterprise / Team SQL Access Control:**
   * Prevent catastrophic data loss by requiring admin sign-off on `DELETE`, `UPDATE`, `ALTER`, or `DROP` statements.
   * Provide safe data access to data analysts, support agents, and junior software engineers without leaking raw database credentials.

2. **Secure Database Bastion Alternative:**
   * Instead of exposing database ports (`3306`, `5432`) over public IPs or managing complex SSH bastion jump hosts, expose only the GateDB HTTPS web interface.

3. **Multi-Engine Personal Database Workspace:**
   * Run and inspect queries across PostgreSQL, MySQL, and SQLite databases in a single tabbed browser interface.
   * Save reusable SQL queries and notes per user with the built-in Sandbox Notes scratchpad.

4. **Cloud Computing & DevOps Teaching Tool:**
   * A complete, working reference project for teaching containerization, persistent volume storage, load balancing, health check mechanisms, reverse proxies, and auto-scaling fleets.

---

## 🔬 Experimental Labs & Hands-On Scenarios

GateDB was built to be extended and experimented with. Here are 6 concrete hands-on experiments you can conduct:

### Experiment 1: Chaos Engineering & Auto-Healing
* **Hypothesis:** When an active container or instance crashes, the application automatically recovers without losing user data or pending approvals.
* **Method:**
  1. Register a user and submit a query in GateDB.
  2. Kill the container (`sudo docker kill gatedb`) or terminate the EC2 instance from the AWS console.
  3. Observe Docker's `--restart always` policy or the AWS Auto Scaling Group launching a replacement node.
  4. Verify that all SQLite databases in `~/gatedb_data` mount cleanly with zero state loss.

### Experiment 2: Load Testing & Auto-Scaling Triggering
* **Hypothesis:** High traffic triggers Amazon CloudWatch threshold alarms and Auto Scaling scale-out events.
* **Method:**
  1. Install a load-testing tool like Apache Benchmark (`ab`) or Locust:
     ```bash
     ab -n 10000 -c 50 http://<YOUR-ALB-DNS>/health
     ```
  2. Watch Amazon CloudWatch `CPUUtilization` metric rise above 70%.
  3. Observe the CloudWatch Alarm transitioning from `OK` to `ALARM` state, prompting the Auto Scaling Group to spin up a second instance.

### Experiment 3: Database Engine Performance Benchmarking
* **Hypothesis:** Execution overhead through GateDB's connectors is negligible compared to raw native clients.
* **Method:**
  1. Configure credentials for a remote MySQL instance, remote PostgreSQL instance, and local SQLite database in `/settings`.
  2. Execute queries of varying complexity (`SELECT *` with 10,000 rows, table joins, index scans).
  3. Benchmark latency, memory consumption, and error handling across each engine connector.

### Experiment 4: SQL Injection & Governance Rule Auditing
* **Hypothesis:** Admin review prevents dangerous statements from executing on target infrastructure.
* **Method:**
  1. Attempt submitting destructive queries (e.g. `DROP TABLE users;--` or `UPDATE accounts SET balance = 1000000;`).
  2. Test the Admin approval interface: inspect how dangerous queries are surfaced, flagged, or rejected with customized rejection messages back to the requester.

### Experiment 5: Reverse Proxy & Header Spoofing (ProxyFix Verification)
* **Hypothesis:** Deploying behind an ALB or Nginx correctly maps `X-Forwarded-Proto` and `X-Forwarded-For` without redirection loops.
* **Method:**
  1. Toggle `ProxyFix(app.wsgi_app, x_for=1, x_proto=1)` in `practice.py`.
  2. Inspect redirects produced by `@login_required` when accessing via HTTP vs HTTPS.
  3. Verify that client IP logging reflects the end-user rather than the ALB private IP.

### Experiment 6: Zero-Downtime Database Migration (SQLite to Amazon RDS)
* **Hypothesis:** GateDB's queue and authentication layers can be seamlessly decoupled from local SQLite and pointed to an Amazon RDS PostgreSQL instance for infinite multi-node scalability.
* **Method:**
  1. Launch an Amazon RDS PostgreSQL `db.t3.micro` instance.
  2. Swap SQLite calls in `Auth/` to utilize `connectors/postgres_conns.py`.
  3. Eliminate the need for local host volume mounts across Auto Scaling instances.

---

## 🗄 Supported Database Engines

| Engine | Driver / Library | Connector File | Supported Operations |
| :--- | :--- | :--- | :--- |
| **MySQL / MariaDB** | `mysql-connector-python` | [`mysql_conns.py`](practiceflask/connectors/mysql_conns.py) | `SELECT`, `SHOW`, `DESCRIBE`, `INSERT`, `UPDATE`, `DELETE`, `CREATE` |
| **PostgreSQL** | `psycopg2-binary` | [`postgres_conns.py`](practiceflask/connectors/postgres_conns.py) | Full SQL Standard, schema inspection, transaction commits |
| **SQLite** | Python Native `sqlite3` | [`sql_lite_conns.py`](practiceflask/connectors/sql_lite_conns.py) | Local & mounted `.db` files, in-memory execution |

---

## 🚀 Getting Started & Installation

### Option 1: Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone -b aws_way https://github.com/AltFallacy/GateDB.git
   cd GateDB/practiceflask
   ```

2. **Build the production image:**
   ```bash
   docker build --platform linux/amd64 -t gatedb:latest .
   ```

3. **Run the container with persistent storage:**
   ```bash
   mkdir -p ~/gatedb_data
   docker run -d \
     --name gatedb \
     --restart always \
     -p 5000:5000 \
     -e DATA_DIR=/app/data \
     -e SECRET_KEY="your-secure-random-key" \
     -v ~/gatedb_data:/app/data \
     gatedb:latest
   ```

4. **Verify health:**
   ```bash
   curl http://localhost:5000/health
   # Returns: {"status": "healthy"}
   ```
   Open `http://localhost:5000` in your browser.

---

### Option 2: AWS EC2 Cloud Deployment

1. **Launch an EC2 Instance:**
   * AMI: Ubuntu 24.04 LTS (`t2.micro` Free Tier)
   * Security Group: Allow SSH (Port 22) and HTTP (Port 80)
   * Storage: 20 GiB gp3
2. **SSH into your instance & set up Docker + Swap:**
   ```bash
   ssh -i your-key.pem ubuntu@<EC2-PUBLIC-IP>

   # Setup 2GB Swap (prevents memory freeze on 1GB RAM)
   sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile && echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

   # Install Docker
   sudo apt-get update -y && sudo apt-get install -y docker.io git
   sudo systemctl enable --now docker
   sudo usermod -aG docker $USER
   newgrp docker
   ```
3. **Pull and run GateDB:**
   ```bash
   git clone -b aws_way https://github.com/AltFallacy/GateDB.git
   cd GateDB/practiceflask
   docker build -t gatedb:latest .
   mkdir -p ~/gatedb_data
   docker run -d --name gatedb --restart always -p 80:5000 -e DATA_DIR=/app/data -v ~/gatedb_data:/app/data gatedb:latest
   ```
4. Access `http://<EC2-PUBLIC-IP>` in your browser.

---

### Option 3: Local Python Environment

1. **Ensure Python 3.10+ is installed.**
2. **Create and activate a virtual environment:**
   ```bash
   cd GateDB/practiceflask
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Waitress production server:**
   ```bash
   python practice.py
   ```
5. Navigate to `http://localhost:5000`.

---

## ⚙ Configuration & Environment Variables

GateDB supports dynamic runtime configuration through environment variables:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `DATA_DIR` | `.` (local directory) / `/app/data` (Docker) | Path to folder where `auth.db`, `pending_req.db`, and `user_settings.db` are stored. |
| `PORT` | `5000` | The network port the Waitress WSGI server binds to. |
| `SECRET_KEY` | `development-key-1234` | Flask session cryptographic signing key. Change in production! |

---

## 📂 Project Directory Structure

```text
GateDB/
├── deployment_flow_diagram.xml       # Full AWS Architecture & Deployment Flow (Draw.io format)
├── README.md                         # Project documentation and experimental lab manual
├── requirements.txt                  # Minimal root runtime dependencies
├── practiceflask/
│   ├── Dockerfile                    # Multi-stage production container manifest
│   ├── .dockerignore                 # Excludes caches, tarballs, and local databases
│   ├── practice.py                   # Main application entry point & Waitress WSGI runner
│   ├── requirements.txt              # Production Linux dependencies (UTF-8)
│   ├── Auth/
│   │   ├── db_config.py              # Dynamic database path manager (DATA_DIR handler)
│   │   ├── create_authdb.py          # User table schema & user insertion logic
│   │   ├── check_authdb.py           # Authentication & password verification
│   │   ├── pending_req.py            # Approval queue schema, inserts, approvals/rejections
│   │   ├── user_settings.py          # Encrypted per-user DB configuration manager
│   │   └── user_notes.py             # Persistent scratchpad notes manager
│   ├── connectors/
│   │   ├── mysql_conns.py            # OOP MySQL connection pooling & execution
│   │   ├── postgres_conns.py         # OOP PostgreSQL connection & execution
│   │   └── sql_lite_conns.py         # OOP SQLite query execution
│   ├── users/
│   │   └── User.py                   # Flask-Login User model class
│   ├── templates/                    # Jinja2 HTML5 UI templates
│   │   ├── base.html                 # Master layout template (Dark Mode design system)
│   │   ├── home.html                 # Landing page
│   │   ├── login.html                # User login screen
│   │   ├── signup.html               # Registration screen
│   │   ├── dashboard.html            # SQL query editor & environment selector
│   │   ├── querybox.html             # Admin centralized governance review queue
│   │   ├── my_requests.html          # User query history, approval status & results
│   │   ├── settings.html             # Saved DB connection parameters hub
│   │   └── about.html                # Project documentation & sandbox scratchpad
│   └── static/
│       └── css/
│           └── main.css              # Custom Vanilla Dark-Mode CSS Design System
```

---

## 🔒 Security Model & Engineering Highlights

* **ProxyFix Reverse-Proxy Compliance:** Enables seamless operation behind ALBs and Cloudflare by respecting `X-Forwarded-Proto`, `X-Forwarded-For`, and `X-Forwarded-Host` headers without redirect loops.
* **Zero Hardcoded Secrets:** Administrative target credentials are never kept in source code; they are dynamically queried at execution time from user-defined encrypted configuration stores.
* **Role-Based Access Control (RBAC):** Strict view-level and API-level authorization decorators powered by `Flask-Login` guarantee standard users cannot approve queries or view other users' sensitive requests.
* **Graceful Exception Interception:** Database connection errors and bad SQL syntax are caught at the connector layer, captured into the queue's result record, and displayed gracefully to the requester rather than terminating the server process.
* **Isolated Network Footprint:** Database TCP listening ports (`3306`, `5432`) remain behind internal subnets; only GateDB's HTTP port is accessible to users.

---

## 📄 License
This project is licensed under the MIT License. Feel free to use, modify, and distribute for academic, personal, and enterprise projects.
