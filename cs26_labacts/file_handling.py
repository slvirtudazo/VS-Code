def student_info():
    name = input('\nEnter your name: ')
    age = input('Enter your age: ')
    course = input('Enter your course: ')

    with open('students.txt', 'w') as file:
        file.write(f'Name: {name}\n')
        file.write(f'Age: {age}\n')
        file.write(f'Course: {course}\n')

    print("\nStudent information added successfully to 'students.txt'")
    print("\n--- Student Information ---")
    with open('students.txt', 'r') as file:
        print(file.read())

    print('--- Updated Student Information ---')
    with open('students.txt', 'r') as file:
        print(file.read())
        
    with open('students.txt', 'a') as file:
        file.write('\nThank you!')

student_info()