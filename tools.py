#Create a MCP server.
from mcp.server.fastmcp import FastMCP
#Database connection 
import sqlite3
import json
#Database connection 
con = sqlite3.connect("./database/studentsDB.sqlite3",check_same_thread=False)
#Create an Cursor Object to access the Database
cursor = con.cursor()
#Create an MCP Object.
mcp = FastMCP("Database Agent Crud Example")

#Defining the tools.
@mcp.tool()
def addNewStudent(studentName:str,email:str,course_name:str,course_fees:float)->str:
    '''
     It will insert student name,email,course name & course fees into tables 
     extracted from the prompt.
     To save or enter student details Please use this tool.
    '''
    cursor.execute("insert into students(name,email)values(?,?)",(studentName,email))
    student_id=cursor.lastrowid
    cursor.execute("insert into courses(course_name,course_fees)values(?,?)",(course_name,course_fees))
    course_id=cursor.lastrowid
    cursor.execute("insert into enrollments(student_id,course_id)values(?,?)",(student_id,course_id))
    con.commit()
    rows =cursor.rowcount
    if rows :
        return 'Student successfully Registered with Us'
    else:
        return 'Unable to Insert new Student record'

@mcp.tool()
def getAllStudents():
    '''
     getting all students from the database with their courses and enrollments
     Show/display all students please use this tool.
    '''
    cursor.execute('''
       select students.name,
       students.email,
       courses.course_name,
       courses.course_fees,
       enrollments.enroll_date
       from students inner join enrollments
       on(students.student_id=enrollments.student_id)
       inner join courses on(courses.course_id = enrollments.course_id);
        
''')
    students = cursor.fetchall()
    #Converting into json Datatype.
    data = []
    for student in students:
        data.append({
            "name":student[0],
            "email":student[1],
            "course":student[2],
            "fees":student[3],
            "enrollment_date":student[4]
        })


    return json.dumps(data)
#Count no of students per courses.
#Show students details between enrollment dates
#Show students whose name begins with 's',ends with 'i' and contains 'sal'
@mcp.tool()
def getStudentByCourses():
    '''this will get students per courses from the database
       show/display/view students by course then use this tool 
    '''
    cursor.execute('''
            select 
            count(students.name) as 'No_Of_Students',
            courses.course_name 
            from students inner join enrollments
            on(students.student_id=enrollments.student_id)
            inner join courses on(courses.course_id = enrollments.course_id)
            group by courses.course_name;
        ''')
    students = cursor.fetchall()
    #Converting into json Datatype.
    data = []
    for student in students:
        data.append({
            "No Of Students":student[0],
            "Course":student[1],
        })
    return json.dumps(data)
    

print("MCP tools are running")
mcp.run()
