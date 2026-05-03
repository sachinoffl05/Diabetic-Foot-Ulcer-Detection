package programs;

import java.util.Scanner;

public class reversenumber {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        int b=0;
        while(a>0){
            int c=a%10;
            b=b*10+c;
            a/=10;
        }
        System.out.println(b);
    }
}
