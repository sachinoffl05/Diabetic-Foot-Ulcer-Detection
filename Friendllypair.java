package programs;

import java.util.Scanner;

public class Friendllypair {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        int b=sc.nextInt();
        int c=0,d=0;
        for(int i=1;i<a;i++){
            if(a%i==0){
                c+=i;
            }
        }
        for(int i=1;i<b;i++){
            if(b%i==0){
                d+=i;
            }
        }
        if((c==b)&&(d==a)){
            System.out.println("Yes");
        }
        else{
            System.out.println("No");
        }
    }
}
