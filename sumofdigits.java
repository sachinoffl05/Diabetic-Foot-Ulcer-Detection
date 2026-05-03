package programs;

import java.util.Scanner;

public class sumofdigits {
    public static void main(String[] args) {
        Scanner sc =new Scanner(System.in);
        int n=sc.nextInt();
        int s=0;
        while(n>0){
            int a=n%10;
            s+=a;
            n/=10;
        }
        System.out.println(s);
    }
}
