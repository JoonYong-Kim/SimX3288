/**
 * @fileoverview SimX Util Javascript API
 * @author tombraid@snu.ac.kr
 * @version 0.1.0
 * @since 2024.01.17
 *
 * 여러군데서 사용할 수 있는 Utility 함수들의 집합.
 */

var SimXUtil = function () {

  var getfloat = function(val1, val2) {
    var buf = new ArrayBuffer(4);
    var buf16 = new Uint16Array(buf);
    var num = new Float32Array(buf);
    buf16[0] = val1;
    buf16[1] = val2;
    return Number((num[0]).toFixed(2));
  }

  var getint = function (val1, val2) {
    var buf = new ArrayBuffer(4);
    var buf16 = new Uint16Array(buf);
    var num = new Int32Array(buf);
    buf16[0] = val1;
    buf16[1] = val2;
    return num[0];
  }

  var getcommand = function (val) {
    const command = {
      0: "정지",
      2: "제어권변경",
      401: "1회관수",
      402: "구역관수",
      403: "파라미터관수"
    }

    if (val in command) {
      return command[val];
    } else {
      return "명령코드없음-" + val;
    }
  }

  var getcontrol = function (val) {
    const control = {
      1: "로컬",
      2: "리모트",
      3: "수동"
    }

    if (val in control) {
      return control[val];
    } else {
      return "제어권코드없음-" + val;
    } 
  }

  var getstat = function (val) {
    const stat = {
      0: "정상",
      1: "에러",
      2: "처리불능",
      3: "전압이상",
      4: "전류이상",
      5: "온도이상",
      6: "휴즈이상",
      101: "센서교체요망",
      102: "센서교정요망",
      103: "센서점검필요",
      401: "준비중",
      402: "제공중",
      403: "정지중"
    }

    if (val in stat) {
      return stat[val];
    } else {
      return "상태코드없음-" + val;
    } 
  }

  var getalert = function (val) {
    const alerts = {
      0: "정상",
      1: "고농도 EC",
      2: "저농도 EC",
      3: "고 pH",
      4: "저 pH",
      5: "저유량",
      6: "고온",
      7: "저온", 
      8: "기타경보",
      9: "저수위",
      10: "과부하"
    }

    if (val in alerts) {
      return alerts[val];
    } else {
      return "에러코드없음-" + val;
    } 
  }

  return {
    getfloat: getfloat,
    getint: getint,
    getcommand: getcommand,
    getcontrol: getcontrol,
    getstat: getstat,
    getalert: getalert
  }
}

//module.exports = SimXUtil();

