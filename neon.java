package programs;

import java.util.Scanner;

public class neon {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        int b=a*a;
        int c=0;
        while(b>0){
            int d=b%10;
            c+=d;
            b/=10;
        }
        if(a==c){
            System.out.print("Yes");
        }
        else{
            System.out.println("No");
        }
    }
}
