# Architecture

UniversityApp separates user interaction, core system logic, and file storage. The CLI uses controllers to coordinate actions; the GUI uses the same underlying models, repository, and utilities through its page handlers.

## Code structure

| Location | Responsibility |
| --- | --- |
| `university_app/src/main.py` | Create shared dependencies and start the CLI. |
| `university_app/src/controllers/` | Handle terminal input, menus, and application workflows. |
| `university_app/src/gui/gui_app.py` | Build the Tkinter interface and handle GUI actions. |
| `university_app/src/system/` | Define `Student`, `Subject`, and the central `StudentRepository`. |
| `university_app/src/utils/` | Validate credentials and generate unique IDs. |
| `university_app/src/database/` | Convert model objects to and from JSON and manage file access. |
| `university_app/data/` | Store the shared `students.data` file. |
| `university_app/tests/` | Test individual classes, component integration, and GUI behaviour. |

## Responsibilities and interfaces

**Controllers and GUI:** `UniversityController` routes users to the admin or student menu. After login, `StudentController` creates a `SubjectController`. These controllers coordinate operations rather than implementing file storage. The GUI provides equivalent workflows through page handlers; it does not invoke the terminal controllers.

**Core logic:** `Student` manages personal details and subject enrolments, including the four-subject limit. `Subject` validates marks and grades and provides grade calculation. Keeping these rules outside the interface allows both CLI and GUI to reuse them.

**Central repository:** `StudentRepository` holds the student collection and provides common operations such as `getStudent()`, `getStudents()`, `addStudent()`, `updateStudent()`, and `removeStudent()`. It also exposes existing IDs and email addresses for `IDGenerator` and `Validator`. Other components use these methods instead of accessing the JSON file directly.

**Persistence:** `Database` loads and saves students and their subjects as JSON. Repository read methods return copies; callers modify a retrieved student and pass it to `updateStudent()` to persist the change. Repository write methods save the proposed collection before replacing their current in-memory state.

## Typical operation

Subject enrolment follows this sequence:

```text
CLI controller or GUI handler
  → retrieve a student through StudentRepository
  → generate an ID and create a Subject
  → Student.addSubject() checks the enrolment limit
  → StudentRepository.updateStudent()
  → Database.save() writes students.data
```

Each entry point constructs a database, repository, validator, and ID generator and passes the shared instances to its interface components. This keeps dependencies explicit and allows tests to substitute a mock database or use a temporary data file.
