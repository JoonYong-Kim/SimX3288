
class control_plugin:
    """ 
    DataStore에 들어오는 값을 설정한다. 단, 양액기 로직을 수행한 뒤에 값이 삽입된다.
    이 함수 내에서만 address가 1이 증가되어 들어오는 문제가 있음. 

    :param address: The starting address
    :param values: The new values to be set
    """
    
    def is_stopping(self):
            """
            표준 401번 address의 값을 확인하여 정지중인지 판단한다. 

            Returns:
                bool : 
            """
            # 표준 주소 401 - data 주소 402
            return self.getValues(402, 1) == 403
        
    def to_standard_address(modbus_address):
        """
        modbus의 입력 address를 출력 address로 변환한다.
        Args:
            modbus_address (int): modbus 주소
        Return : 
        
        """
        return modbus_address - 1
    
    def is_operation_control_message(standard_address, value:int):
        """
            address와 value를 보고 operation control message인지 판단한다. 
        Args:
            standard_address (int): 표준에 정의된 address 
            value (int): 401, 402, 403(준비중, 제공중, 정지중)

        Returns:
            bool : operation_control_message인지 여부
        """
        if standard_address == 504 and value in [401, 402, 403]:
            log.debug("Receive operation control message.")
            return True
        return False 

    def is_stop_control_message(standard_address, value:int):
        return standard_address == 604 and value == 0

    def is_stopping_status_message(standard_address, value:int):
        return standard_address == 301 and value == 0
    
    def append_operation_message(queue:deque, modbus_address, values):
        queue.append((modbus_address, values))
        return queue

    def pop_operation_message(queue:deque):
        return queue.popleft()

    def clear_operation_queue(queue:deque):
        queue.clear()


    # 양액기 제어 정보가 들어옴
        # 양액기 상태 정보를 확인

    ## 제어 명령이 들어올 때
        ## 동작 상태가 정지라면, 큐에 넣지 않고 양액기 제어 정보를 삽입
        ## 동작 상태가 작동이라면, 큐에 삽입

    ## 정지 명령이 들어올 때
        ## 큐를 비우고 제어 정보에 정지를 삽입

    ## 양액기 상태가 정지로 바뀔 때
        ## 큐에 명령이 남아있다면, 양액기 제어 정보에 큐를 삽입
standard_address = to_standard_address(address)
log.info("Write value at server address(standard) : " + str(standard_address) + ", values: " + str(values))
decoded_int_value = read_payload(values, int, len(values))
decoded_float_value = read_payload(values, float, len(values))
log.info("decoded values: " + str(decoded_int_value) + ", " + str(decoded_float_value))


#super(DefaultCallbackDataBlock, self).setValues(address, values)
if is_operation_control_message(standard_address, decoded_int_value):
    if self.is_stopping:
        super(DefaultCallbackDataBlock, self).setValues(address, values)
    else:
        append_operation_message(self.operation_queue, address, values)
        return
elif is_stop_control_message (standard_address, decoded_int_value):
    clear_operation_queue(self.operation_queue)
    super(DefaultCallbackDataBlock, self).setValues(address, values)
elif is_stopping_status_message(standard_address, decoded_int_value):
    if self.operation_queue.count != 0:
        waited_address, waited_values = pop_operation_message(self.operation_queue)
        super(DefaultCallbackDataBlock, self).setValues(waited_address, waited_values)
    else:
        super(DefaultCallbackDataBlock, self).setValues(address, values)
else:
    if inspect.isfunction(self.callback_func):
        self.callback_func(address, values)