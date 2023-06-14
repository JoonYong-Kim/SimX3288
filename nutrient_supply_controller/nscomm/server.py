from os import O_APPEND

from typing import List

from collections import deque
from pymodbus.datastore.store import BaseModbusDataBlock
from pymodbus.framer.socket_framer import ModbusSocketFramer
from pymodbus.version import version

from pymodbus.server.asynchronous import StartSerialServer, StartTcpServer

from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder

from pymodbus.transaction import (ModbusRtuFramer,
                                  ModbusAsciiFramer,
                                  ModbusBinaryFramer)

from multiprocessing import Queue, Process, queues
from pymodbus.constants import Endian

import logging
import inspect
import numpy as np

from threading import Lock, Thread
from contextlib import contextmanager


FORMAT = ('%(asctime)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

def read_payload(payload, value_type=int, size=1):
    """
    modbus register에 들어온 payload를 읽는다. 
    value_type은 이 값이 float인지, int인지 구분하며, size는 1일 때 16비트, 2일 때 32비트를 사용한다.
    read_payload는 다음과 같은 유형을 가진다. unsigned 16bit integer, unsigned 32bit integer, unsigned 16bit float, unsigned 32bit integer.

    Args:
        payload (list): 읽어야 할 페이로드
        value_type (type, optional): 읽어올 값의 타입을 의미한다. Defaults to int.
        size (int, optional): 읽어올 값의 사이즈를 의미한다. 16비트 혹은 32비트. Defaults to 1.

    Returns:
        int|float: value_type, size에 따라서 다른 값이 리턴된다. 기본은 16bit unsigned int
    """

    decoder = BinaryPayloadDecoder.fromRegisters(
        payload, byteorder=Endian.Little, wordorder=Endian.Big)

    if value_type is int and size == 2:
        return decoder.decode_32bit_uint()
    elif value_type is float and size == 1:
        return decoder.decode_16bit_float()
    elif value_type is float and size == 2:
        return decoder.decode_32bit_float()
    else:
        return decoder.decode_16bit_uint()


class DefaultCallbackDataBlock(ModbusSequentialDataBlock):
    """
    Slave로부터 데이터를 수신하여 장치를 동작시키기 위한 클래스다.
    ex) 
    data_block = CallbackDataBlock(0x00, [0]*0x400)
    init_server = ({}, data_block)  
    """

    def __init__(self):
        """
        초기화하는 함수이다. 컬백 함수를 인자값으로 넣어서 설정할 수 있다.

        Args:
            callback_func ((address, values)->any, optional): 데이터 호출 시 실행할 함수. Defaults to empty_func.
        """
        super(DefaultCallbackDataBlock, self).__init__(0x00, [0]*0x400)
        self.lock = Lock()

    def set_callback(self, callback):
        """
        슬레이브에서 호출할 콜백함수를 설정한다.

        Args:
            callback (function): 타입이 (address, values) -> Any 인 함수
        """
        self.callback_func = callback

    def setValues(self, address, values):
        log.info("Receive address, value : %s, %s", address, read_payload(values))
        with self.lock:
            super(DefaultCallbackDataBlock, self).setValues(address, values)

    def getValues(self, address, count):
        log.debug("value" + str(self.values))
        value = None
        with self.lock:
            value = super().getValues(address, count=count) 
        return value


def create_modbus_slave_store(data_block):
    return ModbusSlaveContext(hr=data_block)

def create_modbus_server_context(store):
    return ModbusServerContext(slaves=store, single=True)

def start_server(method, context, host=("127.0.0.1",31234), port="/dev/USB0"):

    if method == "tcp":
        conn = StartTcpServer(context, address=host, framer=ModbusSocketFramer)
    elif method == "serial":
        conn = StartSerialServer(context=context,
                                 port=port,
                                 framer=ModbusRtuFramer)
    return conn

def run_server(method, context, host, port):
    thread = Thread(group=None, target=start_server, 
                    kwargs={"method":method,
                            "context":context,
                            "host":host,
                            "port":port})
    thread.start()
    return thread

def write_register_value(store: ModbusSlaveContext, address, value, size=1):
    """
    레지스터에 값을 쓴다. Exception 처리를 하지 않으므로, 이를 호출하는 함수에서 Exception 처리를 수행한다.

    Args:
        store (ModbusSlaveContext): Modbus Slave Context를 처리한다.
        address (int): 값을
        value ([type]): [description]
        size (int, optional): [description]. Defaults to 1.
    """
    WRITE_HOLDING_REGISTER = 6
    builder = BinaryPayloadBuilder(
        byteorder=Endian.Little, wordorder=Endian.Big)

    if type(value) is int and size == 2:
        builder.add_32bit_uint(value)
    elif type(value) is float and size == 1:
        builder.add_16bit_float(value)
    elif type(value) is float and size == 2:
        builder.add_32bit_float(value)
    else:
        builder.add_16bit_uint(value)

    store.setValues(WRITE_HOLDING_REGISTER, address, builder.to_registers())


def set_node_infomation(store, 
                        certification=0,
                        company_code=1,
                        product_type=3,
                        product_code=4,
                        protocol_version=20,
                        channel=21,
                        serial=0):
    """
    Modbus 서버가 만들어지면 노드 정보를 설정할 수 있다.

    호출 함수 read_holding_registers(address, count=1)
    기관코드 : read_holding_registers (1,1) 0일 경우로 가정하고  표준의 부속서 A를 사용
    회사코드 : read_holding_registers (2,1) 0일 경우로 가정하고 표준의 부속서 A를 사용
    제품 타입 : read_holding_register(3,1) 3일 경우로 가정
    제품 코드 : read_holding_register(4,1) 1,2,3,4 등으로 가정
    프로토콜 버전 : read_holding_register(6,1) 20을 기술
    채널 수 : read_holding_register(6,1) 부착 가능한 디바이스의 수 
    시리얼 번호 : read_holding_register(7, 2)

    """
    if store is None:
        return

    if certification != None:
        write_register_value(store, 1, certification)
        
    if company_code != None:
        write_register_value(store, 2, company_code)
    
    if product_type != None:
        write_register_value(store, 3, product_type)
    
    if product_code != None:
        write_register_value(store, 4, product_code)
        
    if protocol_version != None:
        write_register_value(store, 5, protocol_version)
        
    if channel != None:
        write_register_value(store, 6, channel)
        
    if serial != None:
        write_register_value(store, 7, serial, 2)


def set_device(store, register_number, code):
    """
    장치를 제어하기 위한 정보를 얻을 번지를 등록한다.
    Modbus 레지스터의 값이 12일 땐 EC 센서, 값이 16일 때는 pH 센서, 값이 5일 때는 구역 유량 센서이며 이 센서들만을 처리한다. 
    레지스터 주소는 101부터 200번까지로 예약되어 있다.  

    Args:
        server_info ([type]): 서버 정보
        register_number([int]): 등록 번호(1~100)
    """
    if register_number < 1 or 100 < register_number:
        return

    if code:
        write_register_value(store, register_number + 100, code)


def set_node_status(store, node_status=0,opid=0,control_status=1):
    """
    양액기 노드의 상태를 등록한다. 양액기 노드 상태는 레지스터 주소인 201, 202, 203에 있다. 

    Args:
        server_info (dict): 서버 정보
        NodeStatus: 노드 상태, 표준 부속서 B.3의 상태 코드 참조
        OperationID : 제어 명령 ID
        ControlStatus :  노드의 제어권 상태 정보, 표준 부속서 B.4의 제어권 상태 및 설정 코드 참조
    """
    if node_status != None:
        write_register_value(store, 201, node_status)
    
    if opid != None:
        write_register_value(store, 202, opid)
    
    if control_status != None:
        write_register_value(store, 203, control_status)


def set_nutrient_status(store, activation_status, area, alert, opid):
    """
    레지스터에 양액기의 상태를 등록한다. 레지스터의 주소는 401~404까지 있다. 

    Args:
        server_info : 양액기 서버 정보
        status : 부속서 B.3 참조
        IrrigationArea : 0
        AlertInfo : 경보
    """
    if activation_status != None:
        write_register_value(store, 401, activation_status)
        
    if area != None:
        write_register_value(store, 402, area)
        
    if alert != None:
        write_register_value(store, 403, alert)
        
    if opid != None:
        write_register_value(store, 404, opid)
        
def get_node_control(store):
    """
    레지스터에 저장된 양액기 제어 정보를 읽는다. write_registers 함수를 사용하여 레지스터에 값을 설정하면, Device가 이를 수신한다.
    Args:
        clientInfo (dict): 양액기 노드 정보
    """

    return {"cmd": store.getValues(3, 501, 1),
            "opid": store.getValues(3, 502, 1),
            "control": store.getValues(3, 503, 1)}


def get_nutrient_control(store):
    """
    레지스터에 저장된 양액기 제어 정보를 읽는다. write_registers 함수를 사용하여 레지스터에 값을 설정하면, Device가 이를 수신한다.
    Args:
        clientInfo (dict): 양액기 노드 정보
    """

    return {"cmd": store.getValues(3, 504, 1),
            "opid": store.getValues(3, 505, 1),
            "start-area": store.getValues(3, 506, 1),
            "stop-area": store.getValues(3, 507, 1),
            "on-sec": store.getValues(3, 508, 2),
            "EC": store.getValues(3, 510, 2),
            "pH": store.getValues(3, 512, 2)}


def set_sensor_status(store, address, value, status):
    """
    센서의 상태 정보를 설정한다.

    Args:
        server_info (dict): 센서 정보를 저장할 store가 있는 server 객체
    """

    if value != None:
        write_register_value(store, address, value, 2)

    if status != None:
        write_register_value(store, address+2, status)


if __name__ == "__main__":
    
    data_block = DefaultCallbackDataBlock()
    store = create_modbus_slave_store(data_block)
    server_context = create_modbus_server_context(store)
    set_node_infomation(store,
                        certification=0,
                        company_code=0,
                        product_type=3,
                        product_code=4,
                        protocol_version=20,
                        channel=21,
                        serial=0)
    thread = run_server("tcp", server_context,("127.0.0.1", 23334), None)
    set_node_infomation(store,
                        certification=0,
                        company_code=0,
                        product_type=3,
                        product_code=4,
                        protocol_version=20,
                        channel=21,
                        serial=0)
    thread.join()