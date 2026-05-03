package programs;

import java.util.Scanner;

public class Binarytriangle {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        for(int i=1;i<=a;i++){
            for(int k=i;k<=a;k++){
                System.out.print(" ");
                }
            for(int j=1;j<=i;j++){
                if((i+j)%2==0){
                System.out.print("1 ");
                }
                else{
                System.out.print("0 ");
                }
            }
            System.out.println();
        }
    }
}
