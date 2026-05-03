package programs;

import java.util.Scanner;

public class perfectsquare {
     public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        int b=(int)Math.sqrt(a);
        if(b*b==a){
            System.out.println("Yes");
        }
        else{
            System.out.println("No");
        }
    }
}
