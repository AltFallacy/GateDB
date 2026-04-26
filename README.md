# GateDB - Secure SQL Governance & Local Client

**GateDB** is a robust, standalone web-based SQL client and enterprise governance tool built in Python. Designed as a dual-threat application, GateDB serves both as a centralized query-approval gateway for organizations and a high-speed personal SQL client for individual developers.

---

##  Architecture

GateDB operates on a unique "Distributed Tool" architecture with two distinct environments:

### 1. Admin Central (The Governance Portal)
*   **The Problem:** Direct database access is dangerous. Giving developers raw credentials to a central production database risks data loss, accidental `DROP` tables, and security breaches.
*   **The Solution:** GateDB acts as the secure middleman. Users submit SQL queries through the web interface without ever seeing the database password. 
*   **The Queue:** Queries enter an SQLite approval queue (`pending_req.db`). An Admin reviews the query inside the dashboard and clicks "Approve" or "Reject". 
*   **Execution:** Once approved, GateDB executes the query on the target database on behalf of the user, captures the output, and returns the result safely to the user's dashboard.

### 2. My Personal (The Local SQL Client)
*   **The Feature:** Users can bypass the Admin queue entirely for their own local databases.
*   **Execution:** Users save their local database credentials in the secure GateDB Settings (`user_settings.db`). When they submit a query specifically targeting "My Personal", GateDB executes it instantly on their machine and returns the result, acting as a lightweight, dark-mode alternative to heavy clients like DBeaver or PGAdmin.

---

##  Security & Engineering First

*   **Zero Hardcoded Credentials**: Administrative credentials are dynamically fetched from encrypted user settings, ensuring source code is production-ready.
*   **No Direct Port Access**: Users interface *only* with the Flask web UI. TCP Database ports (`3306`, `5432`) are hidden securely behind the backend.
*   **Graceful Error Catching**: Bad SQL syntax triggers a graceful failure, rejecting the request and displaying the engine error log to the user safely, rather than crashing the server.
*   **Role-Based Access Control**: Strict RBAC powered by `Flask-Login` separates Admin privileges (queue approval, instant `Admin Central` execution) from standard Users.
*   **Robust DB Connectors**: Custom Python OOP connectors capable of fetching data across `SELECT`, `SHOW`, `DESCRIBE`, and `EXPLAIN` queries while committing standard CRUD operations.

---

##  Tech Stack
*   **Backend:** Python 3.12, Flask, SQLAlchemy, Waitress (Production WSGI Server)
*   **Database Engines:** MySQL (`mysql-connector-python`), PostgreSQL (`psycopg2-binary`), SQLite (`sqlite3`)
*   **Frontend:** HTML5, CSS3 (Custom Vanilla Dark Mode Design System), Vanilla JS
*   **Distribution:** PyInstaller (Standalone `.exe` generation)

---

##  Installation & Usage

### Option 1: Standalone Windows Executable (Recommended)
You do not need Python installed to run GateDB.
1. Download `GateDB.exe` from the Releases page.
2. Double-click to launch. It will automatically start the Waitress production server on your local network.
3. Open your browser and navigate to `http://localhost:5000`.

### Option 2: Run from Source
1. **Clone the repository and install dependencies:**
   ```bash
   git clone <repo-url>
   cd GateDB/practiceflask
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the Waitress Server:**
   ```bash
   python practice.py
   ```

---

## Configuration & UI Features

*   **Settings Hub:** Upsert and delete configurations per database engine.
*   **Sandbox Notes:** A persistent, user-specific text area on the About page to save helpful SQL snippets.
*   **Instant Copy:** 1-click clipboard copying for returned query results.
*   **Micro-Animations:** Clean, responsive feedback for button clicks, table hovers, and status badges.
