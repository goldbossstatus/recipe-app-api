mystring = '1,2,3'
# print([int(str_id) for str_id in mystring.split(',')])
new_string = mystring.split(',')
neww = []
for x in new_string:
    neww.append(int(x))
print(neww)
