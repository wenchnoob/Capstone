
class PQ:
    def __init__(self):
        self.arr = []

    def add(self, t):
        if (len(self.arr)) <= 0:
            self.arr.append(t)
            return

        arr = self.arr
        ins = False
        for i in range(len(self.arr)):
            if t[0] >= arr[i][0]:
                if t[0] == arr[i][0]:
                    for j in range(len(self.arr)):
                        if t[1] > arr[j][1]:
                            arr.insert(j, t)
                            ins = True
                            break
                else:
                    arr.insert(i, t)
                    ins = True
                    break
                break
        if not ins:
            arr.append(t)

pq = PQ()

c = int(input())

for i in range(c):
    line = input().split()

    if line[0] == 'add':
        _, w, p = line
        w = int(w)
        p = int(p)
        pq.add((w, p))
    else:
        _, e = line
        e = int(e)
        points = 0

        arr = pq.arr.copy()
        toremove = []
        for t in arr:
            if t[0] <= e:
                points += t[1]
                e -= t[0]
                pq.arr.remove(t)

            if e <= 0:
                break

        for t in toremove:
            pq.arr.remove(t)

        print(points)




