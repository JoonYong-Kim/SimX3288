/**
 * @fileoverview SimX Scenario Generator Javascript API
 * @author tombraid@snu.ac.kr
 * @version 0.1.0
 * @since 2024.01.07
 *
 * KS X 3288 표준적합성 검정을 위한 Scenario Generator (SG)
 */

var SimXSG = function () {

  var scenarios = {
    "nutrient-supply/level3": {
      "schema" : [{
        "key": "NODE_CONN",
        "id": "NODE_CONN",
        "name": "노드연결시험",
        "ref": "5.1.1",
        "process": [{
          "command": "confirm",
          "param": {
            "title": "검정장비와 시험대상 노드 연결",
            "message": "검정장비와 시험대상 노드를 RS485 케이블로 연결하고, 슬레이브 아이디를 입력하였다."
          }
        }, {
          "command": "read",
          "param": {
            "address": 1,
            "length": 6
          }
        }]
      }, {
        "key": "NODE_INFO",
        "id": "NODE_INFO",
        "name": "노드정보확인시험",
        "ref": "5.1.2",
        "process": [{
          "command": "read_check",
          "param": {
            "address": 1,
            "length": 6,
            "values": [0, 0, 3, 4, 20, 21],
          },
          "delay": 2
        },{
          "command": "read_check",
          "param": {
            "address": 101,
            "length": 21,
            "values": ["!12", "!12", "!12", "!16", "!16", "!16", "!7", "!5", "!5", "!5", "!5", "!5", "!5", "!5", "!5", "!5", "!5", "!5", "!5", "!5", 204]
          },
          "delay": 2
        }]
      }]
    }, 
    "controller": {
    }
  }

  var getscenario = function(target) {
    return scenarios[target]
  }

  var updatescenario = function(target, scenario, extinfo) {
    return scenarios[target]
  }

  return {
    getscenario: getscenario,
    updatescenario: updatescenario
  }
}

//module.exports = SimXSG();

