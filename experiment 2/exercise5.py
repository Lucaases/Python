digits = [1, 2, 3, 4]
for i in range(len(digits)):
  for j in range(len(digits)):
    for k in range(len(digits)):
      for l in range(len(digits)):
        if i != j and i != k and i != l and j != k and j != l and k != l:
          number = str(digits[i]) + str(digits[j]) + str(digits[k]) + str(digits[l])
          print(number)
