package programs;

import java.util.Scanner;

public class strongnum {
     static int f(int n){
        int c=1;
        for(int i=1;i<=n;i++){
            c=c*i;
        }
        return c;
    }
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        int b=a,c=0;
        while(b>0){
            int d=b%10;
            c+=f(d);
            b/=10;
        }
        if(c==a){
            System.out.println("Yes");
        }
        else{
            System.out.println("No");
        }
    }
}
