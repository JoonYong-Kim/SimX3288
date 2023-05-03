/**
 * @fileoverview SimX UI Javascript API
 * @author tombraid@snu.ac.kr
 * @version 0.1.0
 * @since 2023.05.03
 */

var SimXUI = function () {
  var getfloat = function(val1, val2) {
    return 0;
  };

  var getint = function (val1, val2) {
    return 0;
  };

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
  };
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
  };

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
    };

    if (val in stat) {
      return stat[val];
    } else {
      return "상태코드없음-" + val;
    } 
  };

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
    };

    if (val in alerts) {
      return alerts[val];
    } else {
      return "에러코드없음-" + val;
    } 
  };

  var checkcol = function (list, comp, i, j) {
    if (comp == null)
      return "";
    if (comp[i] != list[i])
      return " class=\"red\" "
    if (j != null && comp[j] != list[j])
      return " class=\"red\" "
    return "";
  };

  var parse = function (list, template, comp) {
    src = ""
    parsed = ""
    for (i = 0, j = 0; i < template.length; i++, j++) {
      src += "<td" + checkcol(list, comp, i, null) + ">" + list[j] + "</td>";
      if (template[i] == "short") {
        parsed += "<td" + checkcol(list, comp, i, null) + ">" + list[j] + "</td>";
      } else if (template[i] == "float") {
        parsed += "<td colspan=\"2\"" + checkcol(list, comp, i, i+1) + ">" + getfloat(list[j], list[j+1]) + "</td>";
        j++;
        src += "<td" + checkcol(list, comp, i, null) + ">" + list[j] + "</td>";
      } else if (template[i] == "int") {
        parsed += "<td colspan=\"2\"" + checkcol(list, comp, i, i+1) + ">" + getint(list[j], list[j+1]) + "</td>";
        j++;
        src += "<td" + checkcol(list, comp, i, null) + ">" + list[j] + "</td>";
      } else if (template[i] == "command") {
        parsed += "<td" + checkcol(list, comp, i, null) + ">" + getcommand(list[j]) + "</td>";
      } else if (template[i] == "control") {
        parsed += "<td" + checkcol(list, comp, i, null) + ">" + getcontrol(list[j]) + "</td>";
      } else if (template[i] == "status") {
        parsed += "<td" + checkcol(list, comp, i, null) + ">" + getstat(list[j]) + "</td>";
      } else if (template[i] == "alert") {
        parsed += "<td" + checkcol(list, comp, i, null) + ">" + getalert(list[j]) + "</td>";
      } else {
        parsed += "<td" + checkcol(list, comp, i, null) + ">" + list[j] + "</td>";
      }
    }
    return src + "</tr><tr>" + parsed;
  };

  var genTable = function (id, header, list, comp, template) {
    html = "<table id=\"" + id + "\" class=\"ui-widget ui-widget-content\"> <thead> <tr class=\"ui-widget-header\">"
    header.forEach (function (col) {
      html += "<th>" + col + "</th>";
    });
    html += "</tr> </thead> <tbody> <tr>";
    html += parse(list, template, comp);
    html += "</tr> </tbody> </table>";

    return html;
  }

  var genNI = function (id, list, comp) {
    header = ["1 기관코드", "2 회사코드", "3 제품타입", "4 제품코드", "5 프로토콜버전", "6 연결가능장비수", "7 시리얼버전(1)", "8 시리얼버전(2)"];
    template = ["short", "short", "short", "short", "short", "short", "int"]

    if (id[0] == 's') {
      html = "<h3>시뮬레이터 노드정보</h3>"
    } else {
      html = "<h3>실장비 노드정보</h3>"
    }
    html += genTable(id, header, list, comp, template);
    return html;
  };

  var genDI = function (id, list, comp) {
    header1 = ["101 EC센서1", "102 EC센서2", "103 EC센서3", "104 pH센서1", "105 pH센서2", "106 pH센서3", "107 일사센서", "108 전체유량센서", "109 1구역유량센서", "110 2구역유량센서"]
    header2 = ["111 3구역유량센서", "112 4구역유량센서", "113 5구역유량센서", "114 6구역유량센서", "115 7구역유량센서", "116 8구역유량센서", "117 9구역유량센서", "118 10구역유량센서" ,"119 11구역유량센서", "120 12구역유량센서", "121 양액기"]
    template1 = Array(10).fill("short")
    template2 = Array(11).fill("short")
    if (id[0] == 's') {
      html = "<h3>시뮬레이터 장비정보</h3>"
    } else {
      html = "<h3>실장비 장비정보</h3>"
    }
    html += genTable(id+"-1", header1, list.slice(0,10), comp, template1);
    html += genTable(id+"-2", header2, list.slice(10,21), comp, template2);
    return html;
  };

  var genNDC = function (id, list) {
    header = ["501 제어명령", "502 명령ID", "503 제어권"]
    template = ["command", "short", "control"]
    if (id[0] == 's') {
      html = "<h3>시뮬레이터 양액기노드 제어정보</h3>"
    } else {
      html = "<h3>실장비 양액기노드 제어정보</h3>"
    }
    html += genTable(id, header, list, null, template);
    return html;
  };

  var genNDS = function (id, list, comp) {
    header = ["201 노드상태", "202 명령ID", "203 제어권상태"]
    template = ["status", "short", "control"]
    if (id[0] == 's') {
      html = "<h3>시뮬레이터 양액기노드 상태정보</h3>"
    } else {
      html = "<h3>실장비 양액기노드 상태정보</h3>"
    }
    html += genTable(id, header, list, comp, template);
    return html;
  };

  var genNSC = function (id, list) {
    header = ["504 제어명령", "505 명령ID", "506 시작구역", "507 종료구역", "508 관수시간(초)1", "509 관수시간(초)2", "510 EC설정1", "511 EC설정2", "512 pH설정1", "513 pH설정2"]
    template = ["command", "short", "short", "short", "int", "float", "float"]
    if (id[0] == 's') {
      html = "<h3>시뮬레이터 양액기 제어정보</h3>"
    } else {
      html = "<h3>실장비 양액기 제어정보</h3>"
    }
    html += genTable(id, header, list, null, template);
    return html;
  };

  var genNSS = function (id, list, comp) {
    header = ["401 양액기상태", "402 관수구역", "403 경보", "404 명령ID", "405 관수남은시간(초)1", "406 관수남은시간(초)2"]
    template = ["status", "short", "alert", "short", "int"]
    if (id[0] == 's') {
      html = "<h3>시뮬레이터 양액기 상태정보</h3>"
    } else {
      html = "<h3>실장비 양액기 상태정보</h3>"
    }
    html += genTable(id, header, list, comp, template);
    return html;
  };

  return {
    genNI: genNI,
    genDI: genDI,
    genNDC: genNDC,
    genNDS: genNDS,
    genNSC: genNSC,
    genNSS: genNSS
  }
};

//module.exports = SimXUI();

