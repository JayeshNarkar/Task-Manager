from project import unused_fun, unused_fun1

def main():
    test_project()

def test_project():
    assert unused_fun(10) == 10
    assert unused_fun(20) == 20
    assert unused_fun(30) == 30
    assert unused_fun(40) == 40
    assert unused_fun(50) == 50
    assert unused_fun(70) == 70
    assert unused_fun(70) == 70
    assert unused_fun(80) == 80
    assert unused_fun(90) == 90
    assert unused_fun(1000) == 1000
    assert unused_fun(1110) == 1110
    assert unused_fun(1102) == 1102

if __name__=="__main__":
    main()