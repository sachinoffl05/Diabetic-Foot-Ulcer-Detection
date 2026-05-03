package programs;

import java.util.Scanner;

public class niven {
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
        if(a%c==0){
            System.out.print("Yes");
        }
        else{
            System.out.println("No");
        }
    }
}
