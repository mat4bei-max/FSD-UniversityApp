# UniversityApp

A university self-enrolment system with a command-line interface (CLI) and a Tkinter graphical interface (GUI). Developed for UTS 32555 Fundamentals of Software Development, Group Cmp1-07.

## Features

- **Students:** register, log in, change passwords, and enrol in or drop up to four subjects. Each enrolment receives a random mark (25–100) and a corresponding grade.
- **Admin:** list students, group them by grade, partition them into pass/fail groups, remove accounts, or clear the database. No admin login is required.
- **Persistence:** student accounts and subjects are saved as JSON in `university_app/data/students.data`, shared by the CLI and GUI. The file is created automatically if missing.

## Getting started

Use Python 3.10 or later, with Tkinter available for the GUI. No third-party packages are required. Run all commands from the project root (`UniversityApp`). On Windows, use `py`; on other systems, use `python3` instead.

| Entry point | Command | Purpose |
| --- | --- | --- |
| CLI: `university_app/src/main.py` | `py -m university_app.src.main` | Open the terminal menu and choose Admin, Student, or Exit. |
| GUI: `university_app/src/gui/gui_app.py` | `py -m university_app.src.gui.gui_app` | Open the graphical application. |

## Rules

### Accounts

| Field | Rule | Example |
| --- | --- | --- |
| Email | Unique address in `firstname.lastname@university.com` format; name parts contain letters A–Z only. | `john.doe@university.com` |
| Name | Must match the email's first and last name. Input is case-insensitive; both names are stored with an initial capital. | `jOHN dOE` becomes `John Doe` |
| Password | At least five letters followed by at least three digits; the first letter must be uppercase. No spaces or special characters. The same rule applies to password changes. | `Abcde123` |
| IDs | Automatically generated strings with leading zeros: six digits for students and three for subjects. | Student `000042`, subject `091` |

### Subjects and results

- A student can enrol in at most four subjects. Dropping a subject frees a place.
- Each enrolment receives a random integer mark from 25 to 100.
- Admin classification uses the unrounded average of currently enrolled subject marks: **PASS** at 50 or above, otherwise **FAIL**. Students with no subjects are **UNGRADED / UNCLASSIFIED**.

| Grade | Mark or average |
| --- | --- |
| Z | Below 50 |
| P | 50 to below 65 |
| C | 65 to below 75 |
| D | 75 to below 85 |
| HD | 85 to 100 |

## Tests

Run the unit, integration, and GUI tests:

```powershell
py -m unittest discover -s university_app/tests -v
```

Tests use temporary data files. GUI tests require a graphical desktop and may briefly display windows.

## Team

Mathis Arthur Beissner, Shivakumar Kothapally, Siddharth Shanbhag, Varun Pocham
