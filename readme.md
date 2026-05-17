# Teachers Attendance Monitor - Markaz Bhikhi

This project automates the scraping of Punjab SIS attendance for **Markaz Bhikhi** schools and generates a report of schools where teacher attendance has not been marked. The script is fully automated with the ability to:

- Run in **headless or normal browser mode**
- Skip specific weekdays or ad-hoc dates
- Automatically rerun until all schools have marked attendance
- Save reports to **both WSL workspace** and **local folder**

---

## 1. Project Structure

```

attendance_monitor/
│
├─ monitor.py                 # Main Python script
├─ README.md                  # Project documentation
├─ teachers_attendance_report.txt  # Local report (generated)
└─ workspace/                 # WSL workspace path
└─ teachers_attendance_report.txt  # WSL report (generated)
└─ dates.txt               # Optional: dates to skip in DD-MM-YYYY format

```

---

## 2. Features

1. **Dynamic School & Markaz Selection**  
   - Configurable `MARKAZ_SCHOOLS` dictionary with Markaz IDs and corresponding school IDs.
   - Only school **names** (no EMIS codes) appear in the report.

2. **Headless Mode**  
   - Use `HEADLESS_MODE = True` for background execution without opening a browser.
   - Set `HEADLESS_MODE = False` to run in a normal visible browser window.

3. **Skipping Days**  
   - `SKIP_WEEKDAYS` allows you to skip attendance check on specific weekdays (`Friday`, `Saturday`, `Sunday` by default).  
   - `dates.txt` file allows skipping specific ad-hoc dates (`DD-MM-YYYY` format).

4. **Automatic Rerun**  
   - The script checks attendance every 10 minutes (`RERUN_INTERVAL`) until all schools have marked attendance or the deadline (`ATTENDANCE_DEADLINE`) is reached.

5. **Dual Report Locations**  
   - WSL workspace report: `\\wsl.localhost\Ubuntu\home\rizwan\.openclaw\workspace\dengue_report\teachers_attendance_report.txt`
   - Local report: `teachers_attendance_report.txt` in the project folder

6. **Report Format**  

```

TEACHERS SIS ATTENDANCE
02:11PM, 17-05-2026

Attendance Pending:
GPS Dera Fakher Din
GPS Longowaal
GPS Dhup Sari
GPS Kudlathi

```

If the day is skipped:

```

TEACHERS SIS ATTENDANCE
02:11PM, 17-05-2026

Attendance Pending:
Attendance check skipped today (weekend or holiday).

````

---

## 3. Configuration Variables

All configurable options are in the top of `monitor.py`:

```python
# Headless mode: True = background, False = normal browser
HEADLESS_MODE = True

# Attendance deadline in 24-hour format
ATTENDANCE_DEADLINE = "16:00"

# Days of week to skip
SKIP_WEEKDAYS = ["Friday", "Saturday", "Sunday"]

# Rerun interval in seconds
RERUN_INTERVAL = 10 * 60

# Markaz and school IDs
MARKAZ_SCHOOLS = {
    '6450': [31925,32015,32017,32033,32034,32035,32044,32045,32049,32441]
}

# WSL workspace directory
WSL_WORKSPACE_DIR = Path(r"\\wsl.localhost\Ubuntu\home\rizwan\.openclaw\workspace\dengue_report")
````

**Note:** Replace your ChromeDriver at:
`C:\Web Drivers\chromedriver.exe` if necessary, and make sure it is compatible with your Chrome version.

---

## 4. Dependencies

* Python 3.8+
* Selenium
* Chrome WebDriver
* pathlib, datetime, time (standard libraries)

Install Selenium if not already:

```bash
pip install selenium
```

---

## 5. Usage

1. Open the script `monitor.py`.
2. Configure the variables at the top (headless, Markaz & schools, deadline, skip weekdays).
3. Place any ad-hoc dates to skip in `dates.txt` (one date per line, `DD-MM-YYYY`).
4. Run the script:

```bash
python monitor.py
```

5. Check the report in **both locations**:

   * Local: `teachers_attendance_report.txt`
   * WSL workspace: `\\wsl.localhost\Ubuntu\home\rizwan\.openclaw\workspace\dengue_report\teachers_attendance_report.txt`

---

## 6. Notes

* The script **automatically reruns every 10 minutes** if there are pending schools.
* Ensure that **ChromeDriver** is installed and in the specified path.
* Adjust **`WINDOW_SIZE`** in headless mode if Highcharts does not render properly.
* Reports include **timestamp** for easy tracking.
* Script can be extended to **append daily reports** instead of overwriting if needed.

---

## 7. Future Enhancements

* Append history of pending schools to a single file for record-keeping.
* Add email notification when pending schools remain.
* Support multiple Markaz dynamically from an external CSV or JSON file.


