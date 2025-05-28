public class Main {
    public static void main(String[] args) {
        Main main = new Main();
        System.out.println(main.getWeight(5));
        System.out.println(main.getWeight(15));
        System.out.println(main.getWeight(25));
        System.out.println(main.getWeight(35));
    }

    String getWeight(int i) {
        if (i == 0) {
            return "no weight";
        }
        if (i <= 10) {
            return "light";
        }
        if (i <= 20) {
            return "medium";
        }
        if (i <= 30) {
            return "heavy";
        }
        return "very heavy";
    }
}