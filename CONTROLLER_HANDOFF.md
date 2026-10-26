# Controller integration notes

## Components and entry points

The three CLI controllers use Mathis's model/repository classes and Shiva's
Database, Validator and IDGenerator. They receive shared instances rather than
opening the data file themselves during menu operations.

| Class | Constructor | Entry point |
| --- | --- | --- |
| StudentController | StudentController(repo, validator, generator) | run() |
| SubjectController | SubjectController(repo, validator, generator) | run(student_id) |
| AdminController | AdminController(repo) | run() |

Each menu returns on x. Admin has no login. Successful student login opens the
SubjectController internally; the university menu should not open it separately.
Importing a controller does not start a menu. Its main block is for independent
CLI testing only.

## Application startup owner

Build these once for the CLI, in this order:

1. Database with the agreed students.data path.
2. StudentRepository.createStudentRepository(database).
3. Validator(repo) and IDGenerator(repo).
4. StudentController(repo, validator, generator) and AdminController(repo).
5. University menu, which calls the appropriate controller's run().

The individual test launchers resolve university_app/data/students.data relative
to their file locations. Use that same absolute path for the integrated CLI and
GUI. Shiva's students.json remains separate development data; changing a path
does not migrate its accounts automatically.

## GUI integration

GUI login should use Validator methods directly, rather than the CLI login()
method, which asks for terminal input and opens a terminal menu.

SubjectController.enrol(student_id) asks for no input and prints nothing. It
returns (subject, enrolled_count) after a successful save, so it can also support
the GUI enrol action. Catch ValueError/OSError and display an exception window.
Student.addSubject enforces the four-subject limit. No successful enrolment
message should be displayed until updateStudent has succeeded.

Get functions return copies: fetch a student, change it through model methods,
then call repo.updateStudent(student). The repository performs the file write.

## Review and validation

The controller menu prompts, credential retry flow and common status messages
were aligned with the assessment's sample I/O. Outputs use plain text, without
terminal colour codes. No sample screenshot contains enough information to
establish that every possible error output must be identical.

Run from the repository root:

```sh
python3 -m unittest discover -s university_app/tests -p test_controllers.py -v
```

13 checks passed on 25 October 2026 using the actual team dependencies and
temporary students.data files. They cover registration, duplicate prevention,
credential retries, login/subject-menu handoff, the subject limit, removals,
password changes, unrounded grade boundaries, admin partitioning, clear
confirmation, menu recovery, reload persistence and reporting a failed save.
The tests do not alter the project's saved accounts.

Individual launch commands for manual testing:

```sh
python3 -m university_app.src.controllers.student_controller
python3 -m university_app.src.controllers.admin_controller
```

## Group decisions still required

- Confirm with the tutor how admin classification should handle fewer than four
  subjects. Current behaviour averages existing subjects; zero-subject students
  are UNGRADED/UNCLASSIFIED to avoid division by zero.
- Connect Varun's university menu and four GUI windows, then run a complete
  demonstration using a shared students.data path. The launcher/GUI were not
  implemented as part of this controller change.
- Test CLI-to-GUI persistence sequentially. Separate repository instances cache
  their own student lists, so simultaneous writes need additional coordination.
- Agree whether to supply fictional demonstration accounts in the final ZIP.
  Local students.data is not included in this controller commit.
- Complete accurate individual contribution records and prepare the compulsory
  showcase. This technical handoff is not an individual authorship declaration.
- Resolve the brief's restriction on AI-generated submission code with the tutor;
  the controller implementation was developed with AI assistance in this chat.
