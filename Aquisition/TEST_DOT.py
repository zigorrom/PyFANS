import numpy as np

def func(a,b,x):
    return a+b*x
l = 4
l2 = 10
a_arr = np.arange(l)
b_arr = np.empty(l,dtype=int)
b_arr.fill(1)
x_arr = np.arange(l*l2).reshape((l2,l)).transpose()

h = np.vstack((a_arr,b_arr))
a_res = a_arr.reshape(1,l).transpose()
print(a_res)
st = np.hstack((a_res, x_arr))

print(st)

print(a_arr)
print(b_arr)
print()
print(x_arr)
print()
print(h)

def af(a):
    print("in_func")
    print(a[1:])
    
    return a[1:] #a# (a[0] + a[-1])*0.5 
    
    
res = np.apply_along_axis(af,1,x_arr)
print(res)
print(x_arr)

##def my_func(a):
##     """Average first and last element of a 1-D array"""
##     return (a[0] + a[-1])*0.5 
##b = np.array([[1,2,3], [4,5,6], [7,8,9]])
##print(b)
##r1 = np.apply_along_axis(my_func, 0, b)
##print(r1)
##r2 = np.apply_along_axis(my_func, 1, b)
##print(r2)
