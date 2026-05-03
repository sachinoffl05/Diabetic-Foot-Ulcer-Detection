
package programs;
import java.util.*;
public class Armstrong {
    public static void main(String[] args) {
        Scanner sc=new Scanner(System.in);
        int a=sc.nextInt();
        int t=a,c=0,s=0;
        while(t>0){
            c++;
            t/=10;
        }
        t=a;
        while(t>0){
            int d=t%10;
            s+=Math.pow(d,c);
            t/=10;
        }
        if(s==a){
            System.out.println("Yes");
        }
        else{
            System.out.println("No");
        }
    }
}
