from src import server, client
from multiprocessing import Queue, Process

import time
import pytest

import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

@pytest.fixture(scope="module")
def run_server():
    server_info:dict = server.init_server(
        server_info={"method": "tcp",
                     "host": ("127.0.0.1", 2882)})
    server.set_node_infomation(server_info,
                               certification=0,
                               company_code=0,
                               product_type=3,
                               product_code=4,
                               protocol_version=20,
                               channel_number=21,
                               serial_number=0)
    server.register_device(server_info, 1, 1)
    server.set_sensor_status_info(server_info, 204, value=3.2, status=1)
    server.set_nutrient_status(server_info, 
                               activation_status=99,
                               area=10,
                               alert=3,
                               opid=12)
    
    log.info(" START Server")    
    p = Process(target=server.start_server, args=(server_info,))
    p.start()
    
    
    yield server_info
    log.info(" TEARDOWN Server")
    p.kill()
    
devinfo = [{
    "id": "1", "dk": "127.0.0.1:2882", "dt": "gw", "children": [{
        "id": "101", "dk": '[1,40201,["status"],45001,["operation","opid"]]', "dt": "nd", "children": [
            {"id": "102", "dk": '[1,40211,["control","status","area","alert","opid"],45001,["operation", "opid", "control","EC","pH", "start-area", "stop-area", "on-sec"]]', "dt": "nutrient-supply/level1"},
            {"id": "103",
             "dk": '[1,204,["value","status"]]', "dt": "sen"},
            {"id": "104",
             "dk": '[1,205,["value","status"]]', "dt": "sen"},
            {"id": "105",
             "dk": '[1,206,["value","status"]]', "dt": "sen"},
            {"id": "106",
             "dk": '[1,207,["value","status"]]', "dt": "sen"},
            {"id": "107",
             "dk": '[1,208,["value","status"]]', "dt": "sen"},
            {"id": "109",
             "dk": '[1,209,["value","status"]]', "dt": "sen"},
            {"id": "110",
             "dk": '[1,210,["value","status"]]', "dt": "sen"},
            {"id": "111",
             "dk": '[1,211,["value","status"]]', "dt": "sen"},
            {"id": "112",
             "dk": '[1,212,["value","status"]]', "dt": "sen"},
            {"id": "113",
             "dk": '[1,213,["value","status"]]', "dt": "sen"}
        ]}
    ], "method": "tcp"}
]

def test_connect(run_server):
    conn = client.connect(method="tcp", host="127.0.0.1", port=2882)
    assert conn is not None
    
def test_read_unit(run_server):
    conn = client.connect(method="tcp", host="127.0.0.1", port=2882)
    assert client.read(conn, 1) is not None

def test_nutrient_node_info(run_server):
    """
    양액기 노드 정보를 클라이언트가 서버로부터 잘 읽어오는지 테스트한다.
    """
    conn = client.connect(method="tcp", host="127.0.0.1", port=2882)
    assert conn is not None
        
    node_info = client.get_node_info(conn, 1)
    
    log.debug("recived node_info : " + str(node_info))
    assert node_info =={
        "certification": 0,
        "company_code": 0,
        "product_type": 3,
        "product_code": 4,
        "protocol_version" : 20,
        "serial_number" : 0,
        "channel_number": 21
    }
    
def test_registered_device_info(run_server):
    """
    노드 부착 디바이스 정보를 잘 가져오는지 테스트한다.
    Args:
        run_server ([type]): [description]
    """
    conn = client.connect(method="tcp", host="127.0.0.1", port=2882)
    
    devices = client.get_devices_info(conn, 1, 2)
    assert devices is not None

    
def test_sensor_status_info(run_server):
    """
    센서 상태 정보를 잘 가져오는지 테스트한다.
    """
    conn = client.connect(method="tcp", host="127.0.0.1", port=2882)
    
    sensor_info = client.get_sensor_status_info(conn,1,  204)
    
    log.debug("recived node_info : " + str(sensor_info))
    assert sensor_info["sensor_value"] < 3.3
    assert 3.1 < sensor_info["sensor_value"]
    assert sensor_info["sensor_status"] == 1
    
def test_nutrient_status_info(run_server):
    """
    양액기 상태 정보를 클라이언트가 읽는 것을 테스트한다.

    Args:
        run_server ([type]): [description]
    """
    inst = client.connect(client_info=client.INITIAL_CLIENT, method="tcp", host="127.0.0.1", port=2882)
    
    nu = client.get_nutrient_status(inst, 1)
    
    assert nu["activation_status"] == 99
    assert nu["area"] == 10
    assert nu["alert"] == 3
    assert nu["opid"] == 12

def test_nutrient_control_info(run_server):
    """
    
    """ 
    inst = client.connect(client_info=client.INITIAL_CLIENT, method="tcp", host="127.0.0.1", port=2882)
    
    client.set_nutrient_control(inst,unit=1, cmd=1, 
                              opid=2, EC=3.3, pH=1.2, 
                              **{"start-area":1, 
                                 "stop-area":3, 
                              "on-sec":2})
    
    time.sleep(1)
    nu = client.get_nutrient_control(inst, 1)
    assert nu["cmd"] == 1
    assert nu["opid"] == 2
    assert nu["start-area"] == 1
    assert nu["stop-area"] == 3
    assert nu["on-sec"] == 2
    assert 3.2 < nu["EC"]
    assert nu ["EC"] < 3.4 
    
def test_node_control_info(run_server):
    """
    
    """ 
    conn = client.connect(client_info=client.INITIAL_CLIENT, method="tcp", host="127.0.0.1", port=2882)
    
    client.set_node_control_info(conn, unit=1, cmd=1, 
                              opid=2, control=1)
    
    time.sleep(1)
    nu = client.get_node_control_info(conn, 1)
    assert nu == {"cmd":1, "opid":2,"control":1}
    
