def walk(s1: str, s2: str, j: int):
    l = len(s1)
    left = True
    right = True

    for i in range(len(s1)):
        if not left and not right:
            return False

        if s1[i] != s2[(j + i) % l]:
            right = False
        if s1[i] != s2[(j - i) % l]:
            left = False

    return left or right


def find_indexes(char, s: str):
    start = 0
    ls = []
    while start != -1:
        start = s.find(char, start)
        if start != -1:
            ls.append(start)
            start += 1
    return ls


def test(s1: str, s2: str):
    if len(set(s1)) != len(set(s2)):
        return False

    start = s1[0]
    indexes = find_indexes(start, s2)

    for i in indexes:
        if walk(s1, s2, i):
            return True

    return False


def check_rotation_or_reverse(passwords: set):
    ls = list(passwords)

    for i in range(len(ls)):
        for j in range(i + 1, len(ls)):
            if test(ls[i], ls[j]):
                return True
    return False


def main():
    l = int(input())
    passwords = set()
    for _ in range(l):
        passwords.add(input())

    if l > len(passwords) or check_rotation_or_reverse(passwords):
        print('Yes')
    else:
        print('No')


main()
