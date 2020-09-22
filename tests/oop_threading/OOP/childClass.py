class Person:
    def __init__(self, person_name, person_age):
        self.name = person_name
        self.age = person_age

    def show_name(self):
        return(self.name)

    def show_age(self):
        return(self.age)


# definition of subclass starts here
class Student(Person):
    studentId = ""

    def __init__(self, student_name, student_age, student_id):
        super().__init__(student_name, student_age)
        self.studentId = student_id

    def get_id(self):
        return self.studentId  # returns the value of student id

if __name__=="__main__":
    s1 = Student('Min Latt', '16', 'id-376')
    print(s1.get_id(), s1.show_name(), s1.show_age())