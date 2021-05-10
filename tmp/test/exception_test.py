
class CustomException(Exception):
    #생성할때 value 값을 입력 받는다.
    def __init__(self, value):
        self.value = value
    
    #생성할때 받은 value 값을 확인 한다.
    def __str__(self):
        return self.value

#예외를 발생하는 함수
def raise_exception(err_msg):
    raise CustomException(err_msg)


#테스트 해보자
try:
    raise_exception("Error!!! Error~!!!")
except CustomException as e:
    print(e)

#Error!!! Error~!!!