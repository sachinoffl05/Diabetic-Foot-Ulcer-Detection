package programs;

import java.util.Scanner;

public class prime {
    public static void main(String[] args) {
        int a,b=0;
        Scanner sc=new Scanner(System.in);
        a=sc.nextInt();
        if(a<=1){
            System.out.println("Not Prime");
        }
        else{
            for(int i=2;i<=a/2;i++){
                if(a%i==0){
                    b=1;
                    break;
                }
            }
        }
        if(b==0){
            System.out.println("Prime");
        }
        else{
            System.out.println("Not Prime");
        }
        }
}
