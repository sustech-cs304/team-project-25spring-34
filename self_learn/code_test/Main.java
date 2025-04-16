public class Main {
    public static void main(String[] args) {
        for (int count = 1; count <= 10; count++) { // loop 10 times
            if (count == 5) // if count is 5
                continue; // skip remaining code in loop
            System.out.printf("%d ", count);
            System.out.println("\nUsed continue to skip printing 5");
        }
    }
}