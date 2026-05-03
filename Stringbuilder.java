import java.util.Scanner;

public class Stringbuilder {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        StringBuilder a=new StringBuilder(sc.nextLine());
        a.reverse();
        System.out.println(a);
    }
}
