def pivots(x,ys):
    if x < min(ys):
        ys.insert(0,x)
        return ys
    elif x > max(ys):
        ys.append(x)
        return ys
    else:
        ys_temp = []
        for i in ys[::-1]:#删除元素需要倒序遍历
            if x >= i:
                ys_temp.append(i)
                ys.remove(i)
        ys_temp1=sorted(ys_temp)       
        sorted_ys = ys_temp1 + [x] + ys
    return sorted_ys

print(pivots(3,[6,4,1,7]))
print(pivots(5,[6,4,1,8,7]))
print(pivots(4,[6,4,1,8,7,2,3,16,11]))