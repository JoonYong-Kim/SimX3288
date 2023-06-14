import logging
import time
import struct
from pymodbus.exceptions import ConnectionException
from pymodbus.other_message import ReadExceptionStatusRequest

from pymodbus.register_read_message import ReadHoldingRegistersResponse

from pymodbus.client.sync import ModbusSerialClient, ModbusTcpClient, BaseModbusClient
from pymodbus.constants import Endian

from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder

from pymodbus.transaction import (ModbusRtuFramer,
                                  ModbusAsciiFramer,
                                  ModbusBinaryFramer,
                                  ModbusSocketFramer)

from lib.mblock import CmdCode, ResCode

FORMAT = ('%(asctime)-15s %(threadName)-15s'
          ' %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

UNIT = 0x01

def connect(host="127.0.0.1", port=2088, method="rtu", **kwargs):
    """
    양액기와 Modbus를 통하여 통신할 수 있도록 연결을 시도한다. 
    파라미터로 포트를 입력받고 나머지는 Default값을 사용한다.
    Timeout은 Mate에 구현된 것을 따른다.
    
    Args:
        client_info ([dictionary]): 위에 기술된 clientState 이며 상태가 업데이트된다.
        port ([string]): example) '/tmp/ptype0'
        baudrate ([integer]): optional
        stopbits ([integer]): 1로 기본적으로 설정
        bytesize ([integer]): 8 로 기본적으로 설정
        timeout ([integer]): 3으로 절정
    
    Return:
    연결이 성공했을 때: 
    {
        "status" : "Connected",
        "client" : <ModbusSerial Client 객체>, 
        "port" : “/tty/USB0”,
    }
    """
    
   
    
    client = None
    if method == "serial":
        client = ModbusSerialClient(method='rtu',framer=ModbusRtuFramer, **kwargs)
    elif method == "tcp":
        client = ModbusTcpClient(host=host, port=port, framer=ModbusSocketFramer)
    
    try:
        client.connect()
    except:
        log.error("Connection Error")
        
    return client

def is_open(conn:BaseModbusClient):
    return conn is not None and conn.is_socket_open()
 
def disconnect(conn:BaseModbusClient):
    """
    양액기와 양액기 클라이언트간의 연결을 해제한다.
    
    Args: client(Dictionary): 클라이언트 정보
    """
    try:
        conn.close()
    except:
        log.error("Closing Error")
    
def decode_register(registers, result_type=int, size=1):
    decoder = BinaryPayloadDecoder.fromRegisters(registers, byteorder=Endian.Little, wordorder=Endian.Big)
    #print("decoded : " + str(decoder.decode_16bit_uint()))
    if result_type == float and size == 1:
        return decoder.decode_16bit_float()
    elif result_type == float and size == 2:
        return decoder.decode_32bit_float()
    elif result_type == int and size == 2:
        return decoder.decode_32bit_uint()
    
    return decoder.decode_16bit_uint()
        

def read(client:BaseModbusClient, unit_id=1, address=1, val_type=int, size=1, default=None):
    """
    register를 읽고 값이 없으면 기본값을 리턴한다. 리턴할 값을 지정해줄 수 있다. timeout을 설정해줄 수 있다.

    Args:
        client_info (client_info): 클라이언트 정보, lock과, client 객체를 담고 있어야 한다. 
        address (int): 주소
        count (int): 읽어들일 메모리 크기
        default (any, optional): 타입은 임의로 들어올 수 있으며, 값을 읽지 못할 경우 기본적으로 리턴할 값이다. Defaults to None.

    Returns:
        any: 읽은 값의 결과
    """
    if address is None:
        return None
    
    if type(address) is str:
        if address.isdigit():
            address = int(address)
        else:
            return None
        
    if address < 1 or address > 550:
        return None
    
    if type(unit_id) is str:
        if unit_id.isdigit():
            unit_id = int(unit_id)
        else:
            return None
        
    if type(size) is str:
        if size.isdigit():
            size = int(size)
        else:
            return None
    
    try:
        response : ReadHoldingRegistersResponse = client.read_holding_registers(address, size, unit=unit_id)
        return decode_register(response.registers, val_type, size)
    except ConnectionException as e:
        log.exception(e)
        log.info("read fail.")
        return default
    return default

def write_instantly(client:BaseModbusClient, unit=1, address=1, value="", size=1):
    builder = BinaryPayloadBuilder(byteorder=Endian.Little, wordorder=Endian.Big)
    
    if type(unit) == str:
        if unit.isdigit():
            unit = int(unit)
        else: raise ValueError
    
    if type(value) is int and size == 2:
        builder.add_32bit_uint(value)
    elif type(value) is float and size == 1:
        builder.add_16bit_float(value)
    elif type(value) is float and size == 2:
        builder.add_32bit_float(value)
    else:
        builder.add_16bit_uint(value)
    
    client.write_registers(address, builder.to_registers(), unit=unit)
        

def write(buffer:dict, address, value, size=1):
    """
    서버에 있는 레지스터에 쓰기 위해서 빌더에 쓰는 역할을 수행한다. 
    Builder가 client_info에 저장되며, 순차적으로 쓰지 않으면 builder가 증가한다. 
    Args:
        client_info (dict): RTU 클라이언트 개체
        address (int): 써야 할 레지스터 번지
        value (int): 주소에 넣을 값

    Returns:
        None
    """
    
    builder_info = None
    builder :BinaryPayloadBuilder = None
    
    # address가 없으면 새로 만듦
    # 현 address + unit 만큼의 값을 키로 등록하고 현 address에 있는 객체를 만들어진 키의 값으로 설정
    # 현 address 삭제
    if address not in buffer:
        builder = BinaryPayloadBuilder(byteorder=Endian.Little, wordorder=Endian.Big)
        builder_info = {
            "builder" : builder,
            "start_address" : address
        }
    else:
        builder_info = buffer[address]
        builder = builder_info["builder"]
        
    t = type(value)
    if t == int and size == 1:
        builder.add_16bit_uint(value)
    elif t == float and size == 2:
        builder.add_32bit_float(value)
    elif t == int and size == 2:
        builder.add_32bit_uint(value)
        
    if address in buffer:
        del(buffer[address])
    buffer[address + size] = builder_info 

def flush(buffer, client, unit=1, ):
    if client == None:
        log.info("client is not created.")
        return ResCode.DISCONNECTED
    
    for recent_address in buffer:
        builder_info = buffer[recent_address]
        start_address = builder_info["start_address"]
        builder : BinaryPayloadBuilder = builder_info["builder"]
        payload = builder.to_registers()
        log.debug("Flush address : " + str(start_address) +", payload : " + str(payload))
        
    res = None
    try:
        res = client.write_registers(start_address, payload, unit=unit)
        log.debug(res)
    except:
        if res.isError():
            log.info("write fail")
        return ResCode.FAIL_TO_WRITE
 
    return ResCode.OK
        

def get_node_info(client, unit):
    """
    Modbus로 연결을 수행하였다면, 다음에는 양액기를 인식해야 한다. 
    양액기를 인식하기 위해서는 레지스터를 읽어야 한다. 
    레지스터는 ModbusSerialClient 객체의 read_holding_register를 호출해야 한다.     
    
    호출 함수 read_holding_registers(address, count=1)
    기관코드 : read_holding_registers (1,1) 0일 경우로 가정하고  표준의 부속서 A를 사용
    회사코드 : read_holding_registers (2,1) 0일 경우로 가정하고 표준의 부속서 A를 사용
    제품 타입 : read_holding_register(3,1) 3일 경우로 가정
    제품 코드 : read_holding_register(4,1) 1,2,3,4 등으로 가정
    프로토콜 버전 : read_holding_register(5,1) 20을 기술
    채널 수 : read_holding_register(6,1) 부착 가능한 디바이스의 수 
    시리얼 번호 : read_holding_register(7, 2)
    
    Args:
        client_info (Dictionary): 클라이언트 정보
    """
    
    if client is None:
        return None
    
    return {
        "certification" : read(client, unit, 1),
        "company_code" : read(client, unit, 2),
        "product_type" : read(client, unit, 3),
        "product_code" : read(client, unit, 4),
        "protocol_version" : read(client, unit, 5),
        "channel_number" : read(client, unit, 6),
        "serial_number": read(client, unit, 7, val_type=int, size=2)
    }
    
def get_devices_info(client, unit, channel_number):
    """
    레지스터로부터 장치 목록을 가져온다. 

    Args:
        client_info (dict): 클라이언트 정보를 가져온다.

    Returns:
        [type]: [description]
    """
    devices = []
    for i in range(1, channel_number + 1):
        devices.append({"register_number": i, 
                        "device_code": read(client, unit, i + 100)})
    return devices

def get_node_status_info(client, unit):
    """
    현재 레지스터에 등록된 양액기 노드의 상태를 확인한다. 
    양액기 노드 상태는 레지스터 주소인 201, 202, 203에 있다. 양액기 노드에 연결이 되어 있어야 확인할 수 있다.
    
    Args:
        client_info ([dict]): 양액기 노드의 상태
    """
    if client is None:
        return None
        
    return {"code" : read(client, unit, 201), # 0~6, 900~
            "opid" : read(client, unit, 202),
            "status" : read(client, unit, 203)} # 1 Local, 2 Remote, 3  manual
    
def get_sensor_status_info(client, unit, address):
    """
    현재 레지스터에 등록된 양액기 센서의 상태를 확인한다. 레지스터 정보는 204로 시작해서 센서 수 X 3(상태, 값) * (16/8) 바이트만큼 존재한다.
    양액기 노드에 연결이 되어 있어야 확인할 수 있다.
    
    Args:
        client_info ([dict]): 양액기 노드 정보
        register_number ([int]): 양액기 센서 ID
    """ 
    if client is None:
        return None
    
    if type(unit) is str:
        if unit.isdigit():
            unit = int(unit)
        else:
            return None
        
    if address is None:
        return None
        
    if type(address) is str:
        if address.isdigit():
            address = int(address)
        else:
            return None
    
        
    return {
        "register_number": address,
        "sensor_value" : read(client, unit_id=unit, address=address, val_type=float, size=2),
        "sensor_status" : read(client, unit, address + 2)
    }

def get_nutrient_status(client, unit):
    """
    레지스터에 등록된 양액기의 상태를 확인한다. 레지스터의 주소는 401~404까지 있다. 양액기 노드에 연결이 되어 있어야 확인할 수 있다.
    
    Args:
        client, unit ([dict]): 양액기 노드 연결 정보
    """
    if client is None:
        return None
    
    return {
        "activation_status" : read(client, unit, 401), #0~99, 401~403, 900~999 401 준비중, 402 제공중,  403 정지중
        "area" : read(client, unit, 402),
        "alert" : read(client, unit, 403), # 0~8
        "opid" : read(client, unit,404)
    }

def set_node_control_info(client, unit, **kwargs):
    """
    양액기 노드의 제어 상태를 설정한다. 레지스터의 주소는 501~503까지 있다. 
    Args:
        client, unit ([dict]): 양액기 노드 연결 정보 
    """  
    if client is None:
        return ResCode.DISCONNECTED
    
    try:
        if "cmd" in kwargs:
            write_instantly(client, unit, 501, kwargs["cmd"])
        
        if "opid" in kwargs:
            write_instantly(client, unit, 502, kwargs["opid"])
            
        if "control" in kwargs:
            write_instantly(client, unit, 503, kwargs["control"])
    except Exception as e:
        log.error(e)
        return ResCode.FAIL_TO_WRITE
    return ResCode.OK
    
    
def get_node_control_info(client, unit):
    """
    레지스터에 등록된 양액기 노드의 제어 상태를 확인한다. 레지스터의 주소는 501~503까지 있다. 양액기 노드에 연결이 되어 있어야 확인할 수 있다.
    Args:
        client, unit ([dict]): 양액기 노드 연결 정보 
    """
    if client is None:
        return None
    
    return {
        "cmd" : read(client, unit, 501),
        "opid" : read(client, unit, 502),
        "control" : read(client, unit, 503)#1,2,3                                                     
    }

def get_nutrient_control(client, unit):
    """
    레지스터에 등록된 양액기의 관수 정보를 확인한다. 레지스터의 주소는 504~513까지 있다. 양액기 노드에 연결이 되어 있어야 확인할 수 있다.
    Args:
        client, unit (dict): 양액기 노드 연결 정보
    """
    if client is None:
        return None
    return {
        "cmd" : read(client, unit, 504), #2 : control, 401 : ON, 0 : OFF, 402 : AREA_ON, 403 : PARAM_ON : 403
        "opid" : read(client, unit, 505),
        "start-area" : read(client, unit, 506),
        "stop-area" : read(client, unit, 507),
        "on-sec" : read(client, unit, 508, size=2),
        "EC" :read(client, unit, 510, val_type=float, size=2),
        "pH" :read(client, unit, 512, val_type=float, size=2),
    }
    
    

def set_nutrient_control(client, unit, **kwargs):
    """
    레지스터에 양액기 제어를 요청한다. get_nutrient_control()의 반대역할을 수행한다. write 함수를 사용하여 레지스터에 값을 설정하면, Device가 이를 수신한다.

    Args:
        client, unit (dict): 연결 정보
    """
    
    if client is None:
        return ResCode.DISCONNECTED
    try:
        if "cmd" in kwargs:
            write_instantly(client, unit, 504, kwargs["cmd"])
        
        if "opid" in kwargs:
            write_instantly(client, unit, 505, kwargs["opid"])
        
        if "start-area" in kwargs:
            write_instantly(client, unit, 506, kwargs["start-area"])
            
        if "stop-area" in kwargs:
            write_instantly(client, unit, 507, kwargs["stop-area"])
            
        if "on-sec" in kwargs:
            write_instantly(client, unit, 508, kwargs["on-sec"], 2)    
        
        if "EC" in kwargs:
            write_instantly(client, unit, 510, float(kwargs["EC"]), 2)
        
        if "pH" in kwargs:
            write_instantly(client, unit, 512, float(kwargs["pH"]), 2)
    except Exception as ex:
        log.error(ex)
        return ResCode.FAIL_TO_WRITE
    return ResCode.OK
    

if __name__ == "__main__":
    client = connect(host="127.0.0.1", port=2882, method="tcp")
    while True:
        print("Nu control : ", get_nutrient_control(client, 1))
        print("Node Info : ", get_node_info(client, 1))
        print("sensor info : ", get_sensor_status_info(client, 1, 204))
        time.sleep(30)
        
    