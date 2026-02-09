using System;
using System.Collections.Generic;

public class ScheduleGenerator
{
    private List<Course> courses = new List<Course>();

    public void AddCourse(Course course)
    {
        foreach (var c in courses)
        {
            if (c.Day == course.Day && c.Time == course.Time)
            {
                Console.WriteLine($"Conflict detected: {course.Name} overlaps with {c.Name}");
                return;
            }
        }

        courses.Add(course);
        Console.WriteLine($"{course.Name} added successfully.");
    }

    public void PrintSchedule()
    {
        Console.WriteLine("\nWeekly Schedule:");
        foreach (var c in courses)
        {
            Console.WriteLine($"{c.Day} {c.Time} - {c.Name} ({c.Instructor})");
        }
    }
}
