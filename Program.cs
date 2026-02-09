using System;
using System.Collections.Generic;

class Program
{
    static void Main()
    {
        Console.WriteLine("Student Schedule Generator");

        var generator = new ScheduleGenerator();
        generator.AddCourse(new Course("Math", "Dr. Smith", "Monday", "09:00"));
        generator.AddCourse(new Course("Physics", "Dr. John", "Monday", "09:00")); // conflict

        generator.PrintSchedule();
    }
}
