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

  var getstat = function (val) {
    const stat = {
      0: "READY",
      1: "ERROR"
    };

    if (val in stat) {
      return stat[val];
    } else {
      return "UNKNOWN STATUS";
    } 
  };

  var parse = function (list, template) {
    parsed = ""
    for (i = 0, j = 0; i < template.length; i++, j++) {
      if (template[i] == "short") {
        parsed += "<td>" + list[j] + "</td>";
      } else if (template[i] == "float") {
        parsed += "<td colspan=\"2\">" + getfloat(list[j], list[j+1]) + "</td>";
        j++;
      } else if (template[i] == "int") {
        parsed += "<td colspan=\"2\">" + getint(list[j], list[j+1]) + "</td>";
        j++;
      } else if (template[i] == "status") {
        parsed += "<td>" + getstat(list[j]) + "</td>";
      } else if (template[i] == "alert") {
        parsed += "<td>" + getalert(list[j]) + "</td>";
      } else {
        parsed += "<td>" + list[j] + "</td>";
      }
    }
    return parsed;
  }

  var genNI = function (pid, id, list) {
    headers = ["1 기관코드", "2 회사코드", "3 제품타입", "4 제품코드", "5 프로토콜버전", "6 연결가능장비수", "7 시리얼버전(1)", "8 시리얼버전(2)"];
    template = ["short", "short", "short", "short", "short", "short", "int"]

    html = "<table id=\"" + id + "\" class=\"ui-widget ui-widget-content\"> <thead> <tr class=\"ui-widget-header\">"
    headers.forEach (function (col) {
      html += "<th>" + col + "</th>";
    });
    html += "</tr> </thead> <tbody> <tr>";
    list.forEach (function (col) {
      html += "<td>" + col + "</td>";
    });
    html += "</tr><tr>";
    html += parse(list, template);
    html += "</tr> </tbody> </table>";
    console.log(html);
    //$("#" + pid).html(html);
    return html;
  }

  return {
    genNI: genNI
  }
};

//module.exports = SimXUI();

