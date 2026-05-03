package programs;

import java.util.Scanner;

public class pascalstriangle {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        int[][] ar=new int[a][a];
        for(int i=0;i<a;i++){
            for(int j=i;j<=a;j++){
                System.out.print(" ");
            }
            for(int j=0;j<=i;j++){
                if(j==0||j==i){
                    ar[i][j]=1;
                }
                else{
                    ar[i][j]=ar[i-1][j-1]+ar[i-1][j];
                }
                System.out.print(ar[i][j]+" ");
            }
            System.out.println();
        }
    }
}
