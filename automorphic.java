package programs;

import java.util.Scanner;

public class automorphic {
     public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        int b=a*a;
        if(b%10==a||b%100==a||b%1000==a||b%10000==a){
            System.out.println("Yes");
        }
        else{
            System.out.println("No");
        }
    }
}
