## My Interfaces for you → Database, Validator, IDGenerator

### Initialization

Create the Database first with the path to the students file, then the StudentRepository, then Validator and IDGenerator with the repository.

Currently the file is `university_app/data/students.json` (JSON). For submission use `students.data` with the same content — just change the path.

```python
database = Database("university_app/data/students.json")
repo = StudentRepository.createStudentRepository(database)
validator = Validator(repo)
generator = IDGenerator(repo)
```

Controllers / GUI should **not** open the students file themselves. Use StudentRepository + these classes.

---

## Database

- StudentRepository has a Database as attribute
- when StudentRepository is created, students are loaded with `database.load()`
- every change goes through StudentRepository set functions, which call `database.save(students)`

- **Database(path)**
- **load() → list[Student]**  
  Returns all students with their subjects. Creates the file and returns `[]` if it does not exist. Returns `[]` if the file is empty.
- **save(list[Student])**  
  Writes the full student list to the file (JSON).
- **clear()**  
  Writes an empty list. The file stays on disk; only the contents are cleared.

JSON structure used in the file (matches Student / Subject attributes):

```json
[
  {
    "student_id": 100001,
    "name": "Alex Lee",
    "email": "alex.lee@university.com",
    "password": "Abcde123",
    "subjects": [
      { "subject_id": 101, "mark": 80, "grade": "D" }
    ]
  }
]
```

Subjects have **no name** — only `subject_id`, `mark`, `grade`.

---

## Validator

Validator gets the StudentRepository as an attribute during initialisation (uses **getAllEmails()** / **getStudents()**).

Failed checks **raise ValueError** — catch them in the controller / GUI and show the message. Do not expect booleans.

- **validateEmail(email)**  
  Must match `firstname.lastname@university.com`
- **validatePassword(password)**  
  Starts with uppercase letter, at least five letters, then three or more digits (e.g. `Abcde123`)
- **ensureNewEmail(email)**  
  Raises if the email is already registered
- **login(email, password) → Student**  
  Returns the matching student, or raises if credentials are wrong

### Working with Validator — Register

```python
validator.validateEmail(email)
validator.validatePassword(password)
validator.ensureNewEmail(email)

student_id = generator.generateStudentId()
student = Student(student_id, name, email, password, [])
repo.addStudent(student)
```

### Working with Validator — Login

```python
student = validator.login(email, password)
# then go to subject enrolment with this student
```

---

## IDGenerator

IDGenerator gets the StudentRepository as an attribute during initialisation in order to use **getAllStudentIDs()** & **getAllSubjectIDs()** so IDs stay unique.

- **generateStudentId() → int**  
  Unique random ID from 1 to 999999 (print as 6 digits if needed, e.g. `000001`)
- **generateSubjectId() → int**  
  Unique random ID from 1 to 999 (print as 3 digits if needed, e.g. `007`)

### Working with Generator — Enrol (same pattern as Mathis)

```python
student = repo.getStudent(student_id)

subject_id = generator.generateSubjectId()
mark = Subject.generateSubjectMark()
grade = Subject.calculateGrade(mark)
subject = Subject(subject_id=subject_id, mark=mark, grade=grade)

student.addSubject(subject)
repo.updateStudent(student)
```

---

## Test data in the file

There are already 10 students in `university_app/data/students.json` for testing login / admin / GUI.

Example login:

- email: `alex.lee@university.com`
- password: `Abcde123`
