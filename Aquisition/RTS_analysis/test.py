Python 3.4.3 (v3.4.3:9b73f1c3e601, Feb 24 2015, 22:44:40) [MSC v.1600 64 bit (AMD64)] on win32
Type "copyright", "credits" or "license()" for more information.
>>> def abc(name , **kw):
	print(name)
	print(**kw)

	
>>> args = {'name': "asdasd",'val':124124}
>>> print(vars(args))
Traceback (most recent call last):
  File "<pyshell#5>", line 1, in <module>
    print(vars(args))
TypeError: vars() argument must have __dict__ attribute
>>> args
{'val': 124124, 'name': 'asdasd'}
>>> vars(args)
Traceback (most recent call last):
  File "<pyshell#7>", line 1, in <module>
    vars(args)
TypeError: vars() argument must have __dict__ attribute
>>> abc(args)
{'val': 124124, 'name': 'asdasd'}

>>> abc(**args)
asdasd
Traceback (most recent call last):
  File "<pyshell#9>", line 1, in <module>
    abc(**args)
  File "<pyshell#3>", line 3, in abc
    print(**kw)
TypeError: 'val' is an invalid keyword argument for this function
>>> def abc(name , **kw):
	print(name)
	print(kw)

	
>>> abc(**args)
asdasd
{'val': 124124}
>>> def func(val):
	print("value is {0}".format(val))
	
