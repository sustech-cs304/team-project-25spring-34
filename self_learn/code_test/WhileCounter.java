public class WhileCounter {
    public static void main(String[] args) {
        int counter = 1; // Control variable (loop counter)
        while (counter <= 10) { // Loop continuation condition
            System.out.printf("%d ", counter);
            ++counter; // Counter increment (or decrement) in each iteration
        }
        System.out.println();
    }
}