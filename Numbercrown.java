package programs;

import java.util.Scanner;

public class Numbercrown {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        for(int i=1;i<=a;i++){
            for(int j=1;j<=i;j++){
                System.out.print(j+" ");
            }
            for(int j=i;j<a;j++){
                System.out.print("  ");
            }
            for(int j=i;j<a;j++){
                System.out.print("  ");
            }
            for(int j=i;j>=1;j--){
                System.out.print(j+" ");
            }
            System.out.println();
        }
    }
}
