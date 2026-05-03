package programs;

import java.util.Scanner;

public class primeinrange {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        int b=sc.nextInt();
        for(int i=a;i<=b;i++){
            int d=0;
            for(int j=2;j<=i/2;j++){
                if(i%j==0){
                    d=1;
                    break;
                }
            }
            if(d==0){
                System.out.print(i+" ");
            }
        }
    }
}
