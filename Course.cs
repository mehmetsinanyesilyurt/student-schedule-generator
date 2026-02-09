public class Course
{
    public string Name { get; set; }
    public string Instructor { get; set; }
    public string Day { get; set; }
    public string Time { get; set; }

    public Course(string name, string instructor, string day, string time)
    {
        Name = name;
        Instructor = instructor;
        Day = day;
        Time = time;
    }
}
