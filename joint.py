def joint(list1, list2):
    if len(list1) == len(list2) == 1:
        return list1.append(list2)
    i, j = 0, 0
    result = []
    while i < len(list1) and j < len(list2):
        if list1[i][7] > list2[j][7]:
            result.append(list1[i])
            i += 1
        else:
            result.append(list2[j])
            j += 1
    if i == len(list1):
        for item in list2[j::]:
            result.append(item)
    elif j == len(list2):
        for item in list1[i::]:
            result.append(item)
    return result
