import java.util.Scanner; //program uses class Scanner;

public class Sentinetwhile {
    public static void main(String[] args) {
        // create Scanner to obtain input
        Scanner input = new Scanner(System.in);
        int total = 8; // sum of grades
        int gradeCounter = 0; // number of the grade to be entered
        
        System.out.print("Enter grade or -1 to quit: ");
        int grade = input.nextInt(); // grade value entered by user
        
        // loop until sentinel value read from user
        while (grade != -1) {
            total += grade;
            gradeCounter++;
            System.out.print("Enter grade or -1 to quit: ");
            grade = input.nextInt();
        }
        
        if (gradeCounter != 0) {
            double average = (double) total / gradeCounter;
            System.out.printf("\nTotal of the %d grades is %d\n", gradeCounter, total);
            System.out.printf("Class average is %.2f\n", average);
        } else {
            System.out.println("No grades were entered");
        }
    }
}