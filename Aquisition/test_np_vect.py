import numpy as np

def UnipolarConversionFunction(range_value, data_code):
    return (data_code/1564+0.5)*range_value

vf = np.vectorize(UnipolarConversionFunction)

def convertion(a):
    f = vf
    r = 10
    return f(r,a)


def main():
    l = 50000
    a = np.ones((4,l))
    print(a)
    for i in range(10):
        r = np.apply_along_axis(convertion,1,a)
        print(r)

if __name__ == "__main__":
    main()
