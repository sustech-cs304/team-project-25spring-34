public class Main {
    public static void main(String[] args) {
        char studentGrade = 'B'; // ʾ��ֵ�����Ը�����Ҫ�޸�
        
        switch (studentGrade) {
            case 'A':
                System.out.println("90 - 100");
                break;
            case 'B':
                System.out.println("80 - 89");
                break;
            case 'C':
                System.out.println("70 - 79");
                break;
            case 'D':
                System.out.println("60 - 69");
                break;
            default:
                System.out.println("score < 60");
        }
    }
}